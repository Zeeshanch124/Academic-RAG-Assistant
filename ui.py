import streamlit as st
from rag_pipeline import build_rag_system, ask_question

st.title("📘 Academic RAG Assistant")

@st.cache_resource
def load_system():
    return build_rag_system()

retriever, llm = load_system()

query = st.text_input("Ask your question:")

if query:
    answer = ask_question(retriever, llm, query)

    st.subheader("Answer")
    st.write(answer)