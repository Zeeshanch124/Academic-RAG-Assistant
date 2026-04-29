from rag_pipeline import build_rag_system, ask_question

print("\n📘 Academic RAG CLI (type 'exit' to quit)\n")

retriever, llm = build_rag_system()

while True:
    query = input("Ask: ")

    if query.lower() == "exit":
        break

    answer = ask_question(retriever, llm, query)

    print("\nAnswer:")
    print(answer)
    print("\n---\n")