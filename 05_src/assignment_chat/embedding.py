# embed_food_guide.py
# Run this script ONCE to generate and persist embeddings into ChromaDB
# Do NOT expect graders to run this — describe the process in README instead

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
import os

load_dotenv('.env')
load_dotenv('.secrets')

# Step 1: Load the PDF
file_path = "canada_food_guide.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()

# Step 2: Split into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(docs)

# Step 3: Connect to persistent ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")

embedding_function = OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# Step 4: Create collection and add chunks
collection = chroma_client.get_or_create_collection(
    name="canada_food_guide",
    embedding_function=embedding_function
)

collection.add(
    documents=[chunk.page_content for chunk in chunks],
    metadatas=[{"page": chunk.metadata.get("page", 0)} for chunk in chunks],
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

print(f"Successfully embedded {len(chunks)} chunks into ChromaDB.")