# tools/tools.py

from langchain.tools import tool
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from utils.logger import get_logger
import os

_logs = get_logger(__name__)

# Initialize persistent ChromaDB client (loaded once at startup)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

embedding_function = OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

food_guide_collection = chroma_client.get_or_create_collection(
    name="canada_food_guide",
    embedding_function=embedding_function
)


@tool
def search_canada_food_guide(query: str, n_results: int = 3) -> str:
    """
    Answers questions about the Canada Food Guide by performing a semantic search
    over the embedded PDF document. Use this tool when the user asks about Canadian
    dietary guidelines, food groups, healthy eating habits, or nutrition recommendations
    from the Canada Food Guide.
    """
    _logs.debug(f"Semantic search query: {query}")

    results = food_guide_collection.query(
        query_texts=[query],
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return "I could not find any relevant information in the Canada Food Guide for your query."

    # Transform retrieved chunks into a natural language response
    formatted_chunks = []
    for i, (doc, meta) in enumerate(zip(documents, metadatas)):
        page_num = meta.get("page", "unknown")
        formatted_chunks.append(f"[Excerpt {i+1} — Page {page_num}]:\n{doc}")

    combined = "\n\n".join(formatted_chunks)

    result = (
        f"Here is what the Canada Food Guide says about '{query}':\n\n"
        f"{combined}\n\n"
        f"Note: This information is sourced from the official Canada Food Guide document."
    )

    _logs.debug(f"Semantic search result: {result}")
    return result