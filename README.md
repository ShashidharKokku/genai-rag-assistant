# GenAI Assistant with RAG

A customer support chatbot powered by Retrieval-Augmented Generation (RAG), built with FastAPI, Gemini, and Sentence Transformers.

---

## Architecture Diagram

```
User Question
     │
     ▼
[Frontend - HTML/CSS/JS]
     │  POST /api/chat
     ▼
[FastAPI Backend - main.py]
     │
     ├──► [RAG Pipeline - rag.py]
     │         │
     │         ├──► [Embeddings - embeddings.py]
     │         │       └── sentence-transformers (all-MiniLM-L6-v2)
     │         │
     │         ├──► [Retrieval - retrieval.py]
     │         │       └── Cosine Similarity Search
     │         │
     │         └──► [LLM - llm.py]
     │                 └── Gemini 1.5 Flash
     │
     └──► [Storage - storage.py]
               └── In-Memory Vector Store
```

---

## RAG Workflow

1. **User sends a question** via the chat UI.
2. **Query embedding** is generated using `all-MiniLM-L6-v2`.
3. **Similarity search** compares query vector against all stored document chunk vectors using cosine similarity.
4. **Top-3 chunks** above a threshold (0.35) are retrieved.
5. **Prompt is built** combining retrieved context + conversation history + user question.
6. **Gemini 1.5 Flash** generates a grounded response.
7. **Response** is returned to the frontend with metadata (chunks retrieved, grounded flag).

---

## Embedding Strategy

- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (local, no API key needed)
- **Why**: Lightweight, fast, runs locally, 384-dimensional embeddings
- **Chunking**: Documents are split into ~400 character chunks with 20% overlap to preserve context across boundaries

---

## Similarity Search Logic

- **Method**: Cosine Similarity via `sklearn.metrics.pairwise.cosine_similarity`
- **Threshold**: 0.35 — queries below this score return "insufficient information"
- **Top-K**: Returns top 3 most relevant chunks

---

## Prompt Design

```
You are a helpful customer support assistant.
Answer using ONLY the provided context.

Context: {retrieved_chunks}
History: {last_5_turns}
Question: {user_question}
Answer:
```

- Temperature set to **0.2** for consistent, factual responses
- If no context is retrieved, the LLM is instructed to acknowledge insufficient information rather than hallucinate

---

## Setup Instructions

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env .env.local
# Edit .env and add your Gemini API key
LLM_API_KEY=your_gemini_api_key_here
```

Get your Gemini API key at: https://aistudio.google.com/app/apikey

### 4. Run the server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 5. Open in browser
```
http://localhost:8000
```

---

## Project Structure

```
project/
├── backend/
│   ├── main.py          # FastAPI entry point, API routes
│   ├── rag.py           # RAG orchestrator
│   ├── embeddings.py    # Embedding generation
│   ├── retrieval.py     # Cosine similarity search
│   ├── llm.py           # Gemini API integration
│   ├── storage.py       # Document chunking + in-memory vector store
│   └── docs.json        # Knowledge base documents
├── frontend/
│   ├── index.html       # Chat UI
│   ├── style.css        # Styles
│   └── script.js        # Frontend logic
├── .env                 # API keys (do not commit)
├── requirements.txt
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a message, get a RAG response |
| GET | `/api/session/new` | Generate a new session ID |
| GET | `/api/health` | Health check |

### POST /api/chat

**Request:**
```json
{
  "sessionId": "abc-123",
  "message": "How do I reset my password?"
}
```

**Response:**
```json
{
  "reply": "You can reset your password from Settings > Security.",
  "sessionId": "abc-123",
  "retrievedChunks": 2,
  "grounded": true
}
```
