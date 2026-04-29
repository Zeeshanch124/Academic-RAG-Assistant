from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
import os

# ---------------------------
# Load PDF safely
# ---------------------------
def build_rag_system(pdf_name="cli_paper.pdf"):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, pdf_name)

    # Load PDF
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    # Split text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(docs)

    # Embeddings (Ollama local)
    embeddings = OllamaEmbeddings(model="llama3")

    # Vector DB
    if os.path.exists("./vector_db"):
        db = Chroma(
            persist_directory="./vector_db",
            embedding_function=embeddings
        )
    else:
        db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./vector_db"
        )

    # Not satisfied with this - want to use retriever interface instead of direct vector store calls
    # retriever = db.as_retriever(search_kwargs={"k": 5})
    # updating retriever to use invoke instead of get_relevant_documents
    retriever = db.as_retriever(
        search_type="mmr",
        persist_directory="./vector_db",
        search_kwargs={
            "k": 8,
            "fetch_k": 20
        }
    )


    # LLM
    llm = Ollama(model="llama3")

    return retriever, llm


# ---------------------------
# Query function (shared)
# ---------------------------
def ask_question(retriever, llm, query):

    docs = retriever.invoke(query)

    # Debug: print retrieved chunks
    for i, d in enumerate(docs):
        print(f"\n--- Chunk {i} ---")
        print(d.page_content)

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
You are an AI assistant answering questions based ONLY on the provided document.

Instructions:
- Use ONLY the context below
- Provide a COMPLETE answer, not just one sentence
- Combine information from multiple parts if available
- Explain clearly in 3-5 lines
- ONLY say "Not found in document" if absolutely no relevant information exists

Context:
{context}

Question:
{query}

Answer:
"""

    return llm.invoke(prompt)


def rewrite_query(q):
    return f"Definition of {q}"