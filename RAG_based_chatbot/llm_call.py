from langchain_ollama import ChatOllama
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever

from langchain_core.prompts import ChatPromptTemplate
from data.embedding_preparation import prepare_vectorstore

def answer_generation(query):
    llm = ChatOllama(model='llama3.2:1b')
    vectorstore = prepare_vectorstore()

    # Step 1 — get all stored chunks as Document list (for BM25)
    all_docs = [
        Document(page_content=vectorstore.docstore._dict[doc_id].page_content)
        for doc_id in vectorstore.index_to_docstore_id.values()
    ]

    # Step 2 — BM25 Retriever (keyword based)
    bm25_retriever = BM25Retriever.from_documents(all_docs)
    bm25_retriever.k = 2

    # Step 3 — FAISS Retriever (vector based)
    faiss_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2}
    )

    # Step 4 — Combine both = Hybrid Search ✅
    hybrid_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],
        weights=[0.5, 0.5]   # 50% BM25 + 50% vector
    )

    results = hybrid_retriever.invoke(query)
    context = '\n\n '.join([doc.page_content for doc in results])
    print('context ------>>>',context)
    # Prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer only based on the context provided. If not found say 'I don't know'."),
        ("human", "Question: {question}\n\nContext: {context}")
    ])

    chain = prompt | llm

    response = chain.invoke({'question':query, 'context':context})
    return response.content


query = "what Martin H. Fischer says?"
print(answer_generation(query))