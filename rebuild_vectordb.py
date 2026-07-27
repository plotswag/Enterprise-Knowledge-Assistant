import os
import shutil

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PDF_FOLDER = "knowledge_base"
VECTOR_DB_PATH = "vector_db"

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load all PDFs
documents = []

for file in os.listdir(PDF_FOLDER):
    if file.endswith(".pdf"):
        path = os.path.join(PDF_FOLDER, file)
        print(f"Loading: {file}")
        loader = PyPDFLoader(path)
        documents.extend(loader.load())

print(f"Loaded {len(documents)} pages")

# Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

# Delete old vector DB
if os.path.exists(VECTOR_DB_PATH):
    shutil.rmtree(VECTOR_DB_PATH)

# Build new FAISS DB
db = FAISS.from_documents(chunks, embeddings)

db.save_local(
    folder_path=VECTOR_DB_PATH,
    index_name="technova_faiss"
)

print("✅ New FAISS database created successfully!")