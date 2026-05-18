from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter   
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(current_dir, "jesc101.pdf")
loader = PyPDFLoader(pdf_path)
docs = loader.load()
# print(docs)

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""])

chunks = splitter.split_documents(docs)
print(chunks)
