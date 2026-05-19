from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter  
from langchain_community.vectorstores import FAISS 
from langchain_ollama import OllamaEmbeddings
import os,re

current_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(current_dir, "jesc101.pdf")
index_path = os.path.join(current_dir,"faiss_index")

def chunk_book(text, chunk_size=500, chunk_overlap=50):

    # Step 1 — split by section headers first
    section_pattern = r'(?=\n\d+(\.\d+)*[\s\t])'
    sections = re.split(section_pattern, text)
    sections = [s.strip() for s in sections if s and s.strip()]

    # Step 2 — further split large sections using RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )

    final_chunks = []
    for section in sections:
        if len(section) > chunk_size:
            # large section → split further
            sub_chunks = splitter.split_text(section)
            final_chunks.extend(sub_chunks)
        else:
            # small section → keep as one chunk
            final_chunks.append(section)

    return sections

def prepare_vectorstore():
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    if os.path.exists(index_path):
        return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    text = '\n '.join([doc.page_content for doc in docs])
    chunks = chunk_book(text, chunk_size=1200, chunk_overlap=100)
    vectorstore = FAISS.from_texts(chunks, embeddings)
    vectorstore.save_local(index_path)

    return vectorstore

