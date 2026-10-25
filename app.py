import streamlit as st
import pymupdf
from openai import OpenAI

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 AI Study Assistant")
st.write(
    "Your personal AI learning companion. Upload study notes "
    "to summarize, generate quizzes, and ask questions."
)

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password"
    )

uploaded_file = st.file_uploader(
    "Upload your study material",
    type=["pdf", "txt"]
)

study_text = ""

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".pdf"):
            with pymupdf.open(
                stream=uploaded_file.getvalue(),
                filetype="pdf"
            ) as document:
                study_text = "\n".join(
                    page.get_text() for page in document
                )
        else:
            study_text = uploaded_file.getvalue().decode(
                "utf-8-sig"
            )

        if study_text.strip():
            st.success("Study material uploaded successfully!")

            with st.expander("Preview your notes"):
                st.text(study_text[:3000])
        else:
            st.warning(
                "No readable text found. Try a text-based PDF or TXT file."
            )

    except Exception as error:
        st.error(f"Could not read the file: {error}")


def ask_ai(instructions, material):
    if not api_key:
        st.error(
            "Please enter your OpenAI API key in the sidebar."
        )
        return None

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-5.5",
            instructions=instructions,
            input=material
        )

        return response.output_text

    except Exception as error:
        st.error(
            "AI request failed. Check your API key, model access, "
            "and API usage limits."
        )
        st.caption(str(error))
        return None


tab1, tab2, tab3 = st.tabs([
    "📝 Summarize Notes",
    "❓ Generate Quiz",
    "💬 Ask AI"
])


with tab1:
    st.subheader("Notes Summarizer")

    if st.button("Generate Summary"):
        if not study_text.strip():
            st.warning("Please upload your study notes first.")
        else:
            with st.spinner("Generating summary..."):
                result = ask_ai(
                    instructions=(
                        "Summarize the supplied study material using "
                        "clear headings, simple language, key points, "
                        "and important definitions. Do not invent facts."
                    ),
                    material=study_text
                )

                if result:
                    st.markdown(result)


with tab2:
    st.subheader("Quiz Generator")

    number_of_questions = st.selectbox(
        "Number of questions",
        [5, 10, 15]
    )

    if st.button("Generate Quiz"):
        if not study_text.strip():
            st.warning("Please upload your study notes first.")
        else:
            with st.spinner("Creating quiz questions..."):
                result = ask_ai(
                    instructions=(
                        f"Create {number_of_questions} multiple-choice "
                        "questions based only on the supplied study "
                        "material. Provide four options for each question, "
                        "the correct answer, and a short explanation. "
                        "If the material is insufficient, say so."
                    ),
                    material=study_text
                )

                if result:
                    st.markdown(result)


with tab3:
    st.subheader("Ask Questions About Your Notes")

    question = st.text_input("Enter your question")

    if st.button("Get Answer"):
        if not study_text.strip():
            st.warning("Please upload your study notes first.")

        elif not question.strip():
            st.warning("Please enter a question.")

        else:
            with st.spinner("Finding your answer..."):
                result = ask_ai(
                    instructions=(
                        "Answer the student's question using only the "
                        "supplied study material. If the answer is not "
                        "present, say that the material does not provide "
                        "enough information. Explain clearly."
                    ),
                    material=(
                        "STUDY MATERIAL:\n"
                        + study_text
                        + "\n\nSTUDENT QUESTION:\n"
                        + question
                    )
                )

                if result:
                    st.markdown(result)


st.divider()

st.caption(
    "AI Study Assistant | Built with Python, Streamlit, and the OpenAI API"
)
