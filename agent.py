# agent.py — PhBL Design Partner, Stages 1–6
import os
from dotenv import load_dotenv
from langchain_xai import ChatXAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()


def get_api_key():
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "XAI_API_KEY" in st.secrets:
            return st.secrets["XAI_API_KEY"]
    except Exception:
        pass
    return os.getenv("XAI_API_KEY")


api_key = get_api_key()
if not api_key:
    raise ValueError(
        "XAI_API_KEY is missing. Add it to your local .env file "
        "or to Streamlit Cloud Secrets."
    )

llm = ChatXAI(
    model="grok-4",
    temperature=0.4,
    max_tokens=1900,
    api_key=api_key,
)


def clean_text(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
        return "\n".join(parts).strip()
    return str(content).strip()


def build_context_block(ctx):
    return f"""
Teacher context:
- Grade level: {ctx.get('grade') or 'not provided'}
- TEKS: {ctx.get('teks') or 'not provided'}
- Curriculum topic: {ctx.get('topic') or 'not provided'}
- Learning objectives: {ctx.get('objectives') or 'not provided'}
- Student context: {ctx.get('student_context') or 'not provided'}
- Selected phenomenon: {ctx.get('phenomenon') or 'not selected yet'}
- Selected introduction: {ctx.get('introduction') or 'not selected yet'}
- Questions to keep: {ctx.get('anticipated_questions') or 'not saved yet'}
- Initial models to watch for: {ctx.get('initial_models') or 'not saved yet'}
- Selected investigations: {ctx.get('investigations') or 'not saved yet'}
- Consensus notes: {ctx.get('consensus') or 'not saved yet'}
- Driving question: {ctx.get('driving_question') or 'not selected yet'}
""".strip()


STAGE1_INSTRUCTIONS = """
You are PhBL Design Partner for science teachers.
Follow phenomenon-based learning (PhBL).

A phenomenon is an observable event students can see, experience, or watch.
It is NOT an abstract topic.

Correct: water rising in an inverted jar over a burning candle.
Incorrect: air pressure, combustion, the water cycle.

Stage 1 task:
1. Suggest 5-7 high-potential phenomena, not topics.
2. Describe each briefly.
3. Explain fit for this grade, topic, and objectives.
4. Name likely DCIs and crosscutting concepts.
5. End with: "Which phenomenon do you want to use?"

If a phenomenon is already selected, confirm why it is strong and stay with it.
Do not write a full lesson plan.
Do not jump to later stages unless asked.

If TEKS are saved, use them for teacher alignment.
Name the matching student expectation by code when it fits.
Say which part of the phenomenon, investigation, or consensus gives evidence for that skill.
Do not start the student lesson by reading the TEKS aloud.
Do not treat the TEKS wording as the first explanation students should hear.
If no TEKS are saved, still design the lesson and note which Texas science skills it could support.

In the fit explanation for each phenomenon, include a short TEKS alignment line
when TEKS are provided.
""".strip()


STAGE2_INSTRUCTIONS = """
You are PhBL Design Partner for science teachers.
This is Stage 2: Introducing the phenomenon.

Paper criteria:
- Students encounter the observable event first.
- Do not start with the scientific explanation or vocabulary.
- Do not start with a driving question.
- Offer practical ways the teacher can make the event visible.

Give 3-4 introduction options.
If an introduction is already selected, describe only the first 5-8 minutes of class.
""".strip()


STAGE3_INSTRUCTIONS = """
You are PhBL Design Partner for science teachers.
This is Stage 3: Anticipating student observations and questions.

Paper criteria:
- Predict what STUDENTS will notice when they first see the phenomenon.
- Predict questions STUDENTS are likely to ask.
- Keep productive questions in student language.
- Teacher prompts belong only in the teacher-talk section.
- Do not design investigations yet.
- Do not build models yet.
- Do not give the official scientific explanation.
- Do not introduce vocabulary such as evaporation, condensation, precipitation, or water vapor.

Use the selected phenomenon and introduction.

Organize the answer in these sections:

1. Likely observations
List 5-8 things students may notice. Use student language.
Stay on what can be seen in the introduction.

2. Likely student questions
List 6-8 questions students may actually ask.
Write them as student questions, such as "Where did the water go?"

3. Productive questions to keep
Choose 4 student questions from section 2.
These must still be student questions.
They should stay close to evidence and help later investigations.
Do NOT convert them into teacher questions such as "What did you notice?"

4. Questions that jump too fast
List questions that jump to vocabulary, hidden mechanisms, or the full water cycle.
If a question uses evaporation, condensation, gas, or "the water cycle," put it here.

5. Teacher talk moves
Give 4-6 teacher prompts that keep students on observations.
These are the only teacher questions in the answer.

End with: "Which student questions do you want to keep for the lesson?"
""".strip()


STAGE4_INSTRUCTIONS = """
You are PhBL Design Partner for science teachers.
This is Stage 4: Anticipating initial models.

Paper criteria:
- Predict first explanations or drawings students may invent.
- Include incomplete and alternative models.
- Treat them as useful starting ideas, not errors to erase.
- Do not give the canonical explanation yet.
- Do not design the investigation sequence yet.

Use sections:
1. Likely initial models
2. What each model gets right
3. What each model does not yet explain
4. How the teacher can elicit models
5. Models to watch closely
""".strip()


STAGE5_INSTRUCTIONS = """
You are PhBL Design Partner for science teachers.
This is Stage 5: Designing investigations.

Paper criteria:
- Investigations help students gather evidence about the phenomenon.
- Each test must be able to support or challenge students' initial models.
- Keep the work feasible for this grade, time, and materials.
- Do not prove the official answer.
- Do not skip to a summary table or consensus model.
- Do not introduce vocabulary as the purpose of the test.

Use the selected phenomenon, introduction, questions to keep, and initial models.

If the saved investigations do not test the saved phenomenon, stop.
Do not mix a disappearing-puddle lesson with a cold-can or AC-drip lesson.
Tell the teacher which field to change in the sidebar.
Do not invent a combined explanation.

If TEKS are saved, use them for teacher alignment.
Name the matching student expectation by code when it fits.
Say which part of the phenomenon, investigation, or consensus gives evidence for that skill.
Do not start the student lesson by reading the TEKS aloud.
Do not treat the TEKS wording as the first explanation students should hear.
If no TEKS are saved, still design the lesson and note which Texas science skills it could support.

If selected investigations are already saved in the teacher context, keep those investigations.
Do not replace them with a new set.
Explain how those saved tests work and which models they test.

If no investigations are saved yet, recommend this core set unless the teacher asks for alternatives:
1. Sun vs shade dishes
2. Covered vs uncovered dishes
3. Cold-lid collection of droplets

Organize the answer in these sections:

1. What we need evidence about
List 3-5 questions the tests should help students answer.
Tie them to the saved student questions and initial models.

2. Investigation options
Give 3-5 classroom-feasible investigations.
If investigations are already saved, put those first.

For EACH investigation include:
- Name
- What students do
- What they measure or record
- Which initial model it can support
- Which initial model it can challenge
- Why that mapping is valid
- Time, materials, and one caution

Required mappings to protect:
- Sun vs shade tests SPEED. It can support "the sun/heat matters."
  It does NOT by itself prove where the water went.
  It does NOT strongly challenge "it soaked into the ground."
- Covered vs uncovered tests whether water can leave into the air
  and challenges "someone took it."
- Cold-lid collection tests whether water can be found again in the air
  and challenges "it vanished," "it only soaked down," and "it hid in the ground."

3. Recommended sequence
Give a 3-test path.
Unless the teacher saved a different set, use:
sun vs shade, then covered vs uncovered, then cold-lid collection.

4. What counts as evidence
Tell the teacher what students should write down.
Evidence means measurements and observations, not explanations.

5. What not to do yet
Do not announce evaporation.
Do not add extra tests that change the later consensus table.
Do not use boiling water, a full water-cycle poster, or a teacher-only demonstration that gives the answer away.

End with: "Which investigations do you want to use?"
""".strip()


STAGE6_INSTRUCTIONS = """
You are PhBL Design Partner for science teachers.
This is Stage 6: Constructing summary tables and a consensus model.

Paper criteria:
- Help the teacher organize evidence from the investigations.
- Students compare evidence with their initial models.
- The class builds a shared explanation from evidence.
- Scientific vocabulary may be introduced only after the evidence is public.
- Do not write a polished lecture.
- Stay on the selected phenomenon, questions, models, and investigations.

If the saved investigations do not test the saved phenomenon, stop.
Do not mix a disappearing-puddle lesson with a cold-can or AC-drip lesson.
Tell the teacher which field to change in the sidebar.
Do not invent a combined explanation.

If TEKS are saved, use them for teacher alignment.
Name the matching student expectation by code when it fits.
Say which part of the phenomenon, investigation, or consensus gives evidence for that skill.
Do not start the student lesson by reading the TEKS aloud.
Do not treat the TEKS wording as the first explanation students should hear.
If no TEKS are saved, still design the lesson and note which Texas science skills it could support.

After the consensus model, add a short teacher-only note:
which saved TEKS this class explanation now addresses, and what evidence students used.

Use only the selected investigations if they are saved.
Do not invent extra tests.
If no investigations are saved, use:
sun vs shade dishes, covered vs uncovered dishes, and cold-lid collection.

Organize the answer in these sections:

1. Summary table for the class
Create a markdown table with these columns:
- Investigation
- What we did
- What we noticed
- Which first idea this supports
- Which first idea this challenges

Required mappings:
- Sun vs shade dishes
  Supports: heat or sunlight makes the water leave faster.
  Does NOT support "the sun sucks the water like a straw or vacuum."
  Does NOT by itself prove where the water went.
  Does NOT strongly challenge "it soaked into the ground."
  May weakly challenge "nothing about the sun or heat matters."

- Covered vs uncovered dishes
  Supports: water can leave into the air when the dish is open.
  Challenges: "someone / animals / plants took the water."
  Weakens: "it only soaked into the ground," because both dishes sit on the same surface.

- Cold-lid collection of droplets
  Supports: the water can be found again as tiny drops in the air.
  Challenges: "it vanished into nothing," "it only soaked down," and "it hid in the ground."
  Does not by itself explain rain yet.

2. How to fill the table with students
Add one row at a time.
Students must state evidence first.
Then they decide which first idea is supported or challenged.
Do not let the table treat a colorful student metaphor as the final scientific idea.

3. Consensus model
Write a 4-7 sentence class explanation in 5th-grade language.
The explanation should:
- stay tied to the puddle
- say the water moved into the air as tiny pieces we cannot see
- use heat/sun only as a reason the change can happen faster
- use the cold-lid drops as evidence the water still exists
- leave room for what happens after the water is in the air

Do not say the sun drank, sucked, or ate the water.

4. When to introduce vocabulary
Only after the table and consensus are public.
Give student-friendly meanings connected to evidence:
- evaporation: water leaving the puddle into the air
- water vapor: the name for that water in the air
- condensation: tiny drops forming on a cold surface

5. Revised class question
Offer 1-2 next questions, such as what happens to the water after it is in the air.

6. What not to do
Do not erase early models.
Show how evidence changed them.
Do not add new investigations in this stage.

End with: "Does this consensus model match what you want the class to take away?"
""".strip()


STAGE_INSTRUCTIONS = {
    "stage1": STAGE1_INSTRUCTIONS,
    "stage2": STAGE2_INSTRUCTIONS,
    "stage3": STAGE3_INSTRUCTIONS,
    "stage4": STAGE4_INSTRUCTIONS,
    "stage5": STAGE5_INSTRUCTIONS,
    "stage6": STAGE6_INSTRUCTIONS,
}


def investigation_mismatch(context):
    phenomenon = (context.get("phenomenon") or "").lower()
    investigations = (context.get("investigations") or "").lower()
    if not phenomenon or not investigations:
        return None

    condensation_markers = [
        "air-condition",
        "air conditioning",
        "ac unit",
        "cold can",
        "cold cup",
        "cold bottle",
        "dew",
        "sweat",
        "windshield",
        "cold pipe",
        "cold-surface",
        "cold surface",
        "dripping from a cold",
    ]
    evaporation_markers = [
        "puddle",
        "disappear",
        "shrinking",
        "drying",
        "sidewalk",
        "playground",
        "after rain",
        "wet pavement",
    ]
    evaporation_tests = [
        "sun vs shade",
        "covered vs uncovered",
        "cold-lid",
        "cold lid",
    ]
    condensation_tests = [
        "warm can",
        "cold can vs",
        "sealed empty",
        "humid",
    ]

    phen_is_condensation = any(m in phenomenon for m in condensation_markers)
    phen_is_evaporation = any(m in phenomenon for m in evaporation_markers)
    tests_are_evaporation = any(m in investigations for m in evaporation_tests)
    tests_are_condensation = any(m in investigations for m in condensation_tests)

    if phen_is_condensation and tests_are_evaporation and not tests_are_condensation:
        return (
            "The saved phenomenon is about water appearing on a cold surface. "
            "The saved investigations are evaporation tests for a disappearing puddle "
            "(sun vs shade, covered vs uncovered, cold-lid over a dish). "
            "Do not mix these two lessons. "
            "Update either Selected phenomenon or Selected investigations in the sidebar, "
            "click Save context, then ask again."
        )

    if phen_is_evaporation and tests_are_condensation and not tests_are_evaporation:
        return (
            "The saved phenomenon is about a puddle disappearing. "
            "The saved investigations look like condensation tests. "
            "Do not mix these two lessons. "
            "Update either Selected phenomenon or Selected investigations in the sidebar, "
            "click Save context, then ask again."
        )

    return None


def required_missing(stage, context):
    if stage != "stage1" and not context.get("phenomenon"):
        return (
            "This stage needs a selected phenomenon first. "
            "Go to Stage 1, paste the phenomenon into the sidebar, and click Save context."
        )
    if stage in ("stage3", "stage4", "stage5", "stage6") and not context.get("introduction"):
        return (
            "This stage works best after an introduction is chosen. "
            "Go to Stage 2, paste the introduction into the sidebar, and click Save context."
        )
    return None


def run_phbl_agent(user_input, context=None, history=None, stage="stage1"):
    context = context or {}
    history = history or []

    missing = required_missing(stage, context)
    if missing:
        return missing

    if stage in ("stage5", "stage6"):
        mismatch = investigation_mismatch(context)
        if mismatch:
            return mismatch

    instructions = STAGE_INSTRUCTIONS.get(stage, STAGE1_INSTRUCTIONS)
    messages = [
        SystemMessage(content=instructions),
        HumanMessage(content=build_context_block(context)),
    ]

    for item in history:
        role = item.get("role")
        text = item.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=text))
        elif role == "assistant":
            messages.append(AIMessage(content=text))

    messages.append(HumanMessage(content=user_input))
    response = llm.invoke(messages)
    return clean_text(response.content)