import json
import os
from backend.embeddings import generate_embeddings_batch

CHUNK_SIZE = 400  # characters per chunk
DOCS_PATH = os.path.join(os.path.dirname(__file__), "docs.json")

# In-memory vector store: list of {"chunk": str, "embedding": list[float]}
vector_store: list[dict] = []


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_len = 0

    for word in words:
        current_chunk.append(word)
        current_len += len(word) + 1
        if current_len >= chunk_size:
            chunks.append(" ".join(current_chunk))
            # Overlap: keep last 20% words for context
            overlap = max(1, len(current_chunk) // 5)
            current_chunk = current_chunk[-overlap:]
            current_len = sum(len(w) + 1 for w in current_chunk)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def load_and_index_documents():
    """Load docs.json, chunk all documents, generate and store embeddings."""
    global vector_store

    with open(DOCS_PATH, "r") as f:
        documents = json.load(f)

    all_chunks = []
    for doc in documents:
        title = doc.get("title", "")
        content = doc.get("content", "")
        full_text = f"{title}. {content}"
        chunks = chunk_text(full_text)
        all_chunks.extend(chunks)

    print(f"[Storage] Indexing {len(all_chunks)} chunks from {len(documents)} documents...")
    embeddings = generate_embeddings_batch(all_chunks)

    vector_store = [
        {"chunk": chunk, "embedding": embedding}
        for chunk, embedding in zip(all_chunks, embeddings)
    ]
    print(f"[Storage] Indexing complete. {len(vector_store)} vectors stored.")


def get_vector_store() -> list[dict]:
    return vector_store
