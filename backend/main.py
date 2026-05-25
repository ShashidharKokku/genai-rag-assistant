from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os

from storage import load_and_index_documents
from rag import rag_pipeline

app = FastAPI(title="GenAI RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: dict[str, list[dict]] = {}
MAX_HISTORY = 5

class ChatRequest(BaseModel):
    sessionId: str
    message: str

class ChatResponse(BaseModel):
    reply: str
    sessionId: str
    retrievedChunks: int
    grounded: bool

@app.on_event("startup")
async def startup():
    load_and_index_documents()

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if not request.sessionId or not request.sessionId.strip():
        raise HTTPException(status_code=400, detail="sessionId is required.")

    session_id = request.sessionId.strip()
    user_message = request.message.strip()
    history = sessions.get(session_id, [])

    try:
        result = rag_pipeline(user_message, history)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": result["reply"]})
    sessions[session_id] = history[-(MAX_HISTORY * 2):]

    return ChatResponse(
        reply=result["reply"],
        sessionId=session_id,
        retrievedChunks=result["retrieved_chunks"],
        grounded=result["grounded"]
    )

@app.get("/api/session/new")
async def new_session():
    return {"sessionId": str(uuid.uuid4())}

@app.get("/api/health")
async def health():
    return {"status": "ok"}

# Serve static files (css, js)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(frontend_path, "index.html"))
