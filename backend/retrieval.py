import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from backend.embeddings import generate_embedding
from backend.storage import get_vector_store

SIMILARITY_THRESHOLD = 0.35
TOP_K = 3


def retrieve_relevant_chunks(query: str) -> tuple[list[str], float]:
    """
    Retrieve top-K most relevant chunks for a query using cosine similarity.
    Returns (list of relevant chunks, best score).
    """
    vector_store = get_vector_store()
    if not vector_store:
        return [], 0.0

    query_embedding = generate_embedding(query)
    query_vector = np.array(query_embedding).reshape(1, -1)

    scored = []
    for item in vector_store:
        doc_vector = np.array(item["embedding"]).reshape(1, -1)
        score = cosine_similarity(query_vector, doc_vector)[0][0]
        scored.append({"chunk": item["chunk"], "score": float(score)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    top_results = scored[:TOP_K]

    best_score = top_results[0]["score"] if top_results else 0.0

    if best_score < SIMILARITY_THRESHOLD:
        return [], best_score

    relevant_chunks = [r["chunk"] for r in top_results if r["score"] >= SIMILARITY_THRESHOLD]
    return relevant_chunks, best_score
