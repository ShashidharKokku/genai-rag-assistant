from backend.retrieval import retrieve_relevant_chunks
from backend.llm import call_llm


def build_prompt(context: str, history: list[dict], question: str) -> str:
    history_text = ""
    for turn in history:
        role = "User" if turn["role"] == "user" else "Assistant"
        history_text += f"{role}: {turn['content']}\n"

    if context:
        prompt = f"""You are a helpful customer support assistant. Answer the user's question using ONLY the provided context below. Be concise and friendly.

Context:
{context}

Conversation History:
{history_text}
User: {question}
Assistant:"""
    else:
        prompt = f"""You are a helpful customer support assistant. You do not have enough information in your knowledge base to answer this question. Politely inform the user and suggest they contact support at support@company.com.

Conversation History:
{history_text}
User: {question}
Assistant:"""

    return prompt


def rag_pipeline(question: str, history: list[dict]) -> dict:
    """
    Full RAG pipeline: retrieve → build prompt → call LLM → return result.
    Returns dict with reply, retrieved_chunks count, and grounded flag.
    """
    chunks, best_score = retrieve_relevant_chunks(question)

    if chunks:
        context = "\n\n".join(chunks)
        grounded = True
    else:
        context = ""
        grounded = False

    prompt = build_prompt(context, history, question)
    reply = call_llm(prompt)

    return {
        "reply": reply,
        "retrieved_chunks": len(chunks),
        "grounded": grounded,
        "best_score": round(best_score, 4)
    }
