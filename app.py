# app.py — PhBL Design Partner, Stages 1–6
import streamlit as st
from agent import run_phbl_agent

def suggest_teks(grade, topic):
    text = f"{grade} {topic}".lower()
    if "5" in text and any(word in text for word in ["water", "weather", "ocean", "evapor", "cycle"]):
        return (
            "5.10A Explain how the Sun and the ocean interact in the water cycle and affect weather.\n"
            "5.1B Ask questions and define problems based on observations or information from text, phenomena, models, or investigations.\n"
            "5.1E Collect observations and measurements as evidence.\n"
            "5.3B Communicate explanations and solutions that connect evidence to scientific ideas."
        )
    return ""

st.set_page_config(page_title="PhBL Design Partner", page_icon="🔬")
st.title("🔬 PhBL Design Partner")
st.caption("Help a science teacher design a phenomenon-based lesson.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = {
        "grade": "",
        "teks": "",
        "topic": "",
        "objectives": "",
        "student_context": "",
        "phenomenon": "",
        "introduction": "",
        "anticipated_questions": "",
        "initial_models": "",
        "investigations": "",
        "consensus": "",
        "driving_question": "",
    }

with st.sidebar:
    st.header("Lesson context")
    grade = st.text_input("Grade level", value=st.session_state.context["grade"])
    teks = st.text_area(
        "TEKS",
        value=st.session_state.context.get("teks", ""),
        help="Paste codes and wording, such as 5.10A. You can add more than one.",
        placeholder="5.10A Explain how the Sun and the ocean interact in the water cycle and affect weather.",
    )
    topic = st.text_input("Curriculum topic", value=st.session_state.context["topic"])    
    objectives = st.text_area("Learning objectives", value=st.session_state.context["objectives"])
    student_context = st.text_area(
        "Student context (optional)",
        value=st.session_state.context["student_context"],
    )
    phenomenon = st.text_input(
        "Selected phenomenon",
        value=st.session_state.context["phenomenon"],
    )
    introduction = st.text_input(
        "Selected introduction",
        value=st.session_state.context.get("introduction", ""),
    )
    anticipated_questions = st.text_area(
        "Questions to keep (optional)",
        value=st.session_state.context.get("anticipated_questions", ""),
    )
    initial_models = st.text_area(
        "Initial models to watch for (optional)",
        value=st.session_state.context.get("initial_models", ""),
    )
    investigations = st.text_area(
        "Selected investigations (optional)",
        value=st.session_state.context.get("investigations", ""),
    )
    consensus = st.text_area(
        "Consensus notes (optional)",
        value=st.session_state.context.get("consensus", ""),
    )

    if st.button("Save context"):
        st.session_state.context = {
            "grade": grade.strip(),
            "teks": teks.strip(),
            "topic": topic.strip(),
            "objectives": objectives.strip(),
            "student_context": student_context.strip(),
            "phenomenon": phenomenon.strip(),
            "introduction": introduction.strip(),
            "anticipated_questions": anticipated_questions.strip(),
            "initial_models": initial_models.strip(),
            "investigations": investigations.strip(),
            "consensus": consensus.strip(),
            "driving_question": st.session_state.context.get("driving_question", ""),
        }
        st.success("Context saved.")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

       
    if st.button("Suggest TEKS from grade and topic"):
        suggested = suggest_teks(grade, topic)
        if suggested:
            st.session_state.context["teks"] = suggested
            st.rerun()
        else:
            st.warning("No built-in match. Paste the TEKS from your scope and sequence.")
            
stage_label = st.radio(
    "Current stage",
    [
        "Stage 1 — Phenomenon",
        "Stage 2 — Introduction",
        "Stage 3 — Observations & questions",
        "Stage 4 — Initial models",
        "Stage 5 — Investigations",
        "Stage 6 — Consensus",
    ],
    horizontal=True,
)

helpers = {
    "Stage 1 — Phenomenon": (
        "stage1",
        "Stage 1 — Phenomenon selection",
        "Suggest observable events, not topics.",
        "Suggest phenomena for this lesson.",
    ),
    "Stage 2 — Introduction": (
        "stage2",
        "Stage 2 — Introducing the phenomenon",
        "Students should see the event before hearing the explanation.",
        "Suggest ways to introduce this phenomenon.",
    ),
    "Stage 3 — Observations & questions": (
        "stage3",
        "Stage 3 — Anticipating observations and questions",
        "Predict what students will notice and ask after they see the phenomenon.",
        "Anticipate student observations and questions.",
    ),
    "Stage 4 — Initial models": (
        "stage4",
        "Stage 4 — Anticipating initial models",
        "Predict first drawings and explanations. Do not correct them yet.",
        "Anticipate students' initial models.",
    ),
    "Stage 5 — Investigations": (
        "stage5",
        "Stage 5 — Designing investigations",
        "Design tests that can support or challenge students' first models.",
        "Suggest investigations for this phenomenon.",
    ),
    "Stage 6 — Consensus": (
        "stage6",
        "Stage 6 — Summary table and consensus model",
        "Organize evidence and build a class explanation.",
        "Build a summary table and consensus model.",
    ),
}

stage, title, helper, placeholder = helpers[stage_label]
st.subheader(title)
st.write(helper)

if st.session_state.context.get("phenomenon"):
    st.info(f"Phenomenon: {st.session_state.context['phenomenon']}")
if st.session_state.context.get("teks"):
    st.info(f"TEKS: {st.session_state.context['teks']}")
if st.session_state.context.get("introduction"):
    st.info(f"Introduction: {st.session_state.context['introduction']}")
if st.session_state.context.get("investigations"):
    st.info(f"Investigations: {st.session_state.context['investigations']}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input(placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Working..."):
            response = run_phbl_agent(
                user_input=prompt,
                context=st.session_state.context,
                history=st.session_state.messages[:-1],
                stage=stage,
            )
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})