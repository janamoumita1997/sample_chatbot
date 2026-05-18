from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter   
import os,re

current_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(current_dir, "jesc101.pdf")
loader = PyPDFLoader(pdf_path)
docs = loader.load()
# print(docs)

# splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""])

# chunks = splitter.split_documents(docs)
# print(chunks)

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

    return final_chunks
