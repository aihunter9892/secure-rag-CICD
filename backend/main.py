from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.rag import stream_answer
import os

# ----------------------------
# Create FastAPI app FIRST
# ----------------------------
app = FastAPI()

# ----------------------------
# CORS (ok for demo)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

# ----------------------------
# Health endpoint (App Runner)
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ----------------------------
# Ask endpoint
# ----------------------------
@app.post("/ask")
def ask(query: Query):
    return StreamingResponse(
        stream_answer(query.question),
        media_type="text/event-stream"
    )

# ----------------------------
# Mount frontend LAST
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_path = os.path.join(BASE_DIR, "frontend")

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")