# main.py
import os
import json
import asyncio
from typing import Optional, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

APP_NAME = os.getenv("APP_NAME", "legalrag-backend")
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app = FastAPI(title=APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskReq(BaseModel):
    question: str
    top_k: int = 6
    session_id: Optional[str] = None
    lang: str = "auto"

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.post("/ask")
async def ask(req: AskReq):
    # DEMO: burada gerçek RAG yerine sabit bir cevap dönüyoruz
    answer = (
        "Demo: Backend çalışıyor. RAG ekleyince cevaplar yalnızca kurum içi belgelere dayanacak."
    )
    citations = [
        {"title": "Demo Kanun", "section": "Madde 1", "date": "2025-01-01", "page": "§1"}
    ]
    return {"answer": answer, "citations": citations, "lang": req.lang}

def sse_event(event: str, data: str) -> bytes:
    return f"event: {event}\ndata: {data}\n\n".encode("utf-8")

@app.get("/ask/stream")
async def ask_stream(request: Request):
    q = request.query_params.get("question", "")
    lang = request.query_params.get("lang", "auto")
    top_k = int(request.query_params.get("top_k", "6"))

    full_answer = (
        "Demo SSE: Akış çalışıyor. RAG entegre edildiğinde yanıtlar iç dokümanlardan üretilecek."
    )
    citations = [
        {"title": "Demo Kanun", "section": "Madde 1", "date": "2025-01-01", "page": "§1"}
    ]

    async def gen():
        for word in full_answer.split():
            if await request.is_disconnected():
                break
            yield sse_event("token", word + " ")
            await asyncio.sleep(0.03)
        yield sse_event("citations", json.dumps(citations, ensure_ascii=False))
        yield sse_event("final", full_answer)
        yield sse_event("end", "done")

    headers = {
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "Content-Type": "text/event-stream; charset=utf-8",
    }
    return StreamingResponse(gen(), headers=headers, media_type="text/event-stream")
