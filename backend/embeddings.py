from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text: str) -> list[float]:
    """Generate embedding vector for a given text."""
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()

def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()
