from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.line_handler import handle_line_webhook
from app.rag_agent import ensure_chain, refresh_index

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ensure_chain()
        print("[startup] Chain loaded successfully")
    except Exception as e:
        print(f"[startup] WARN: ensure_chain failed: {e}")
    yield
    print("[shutdown] App is shutting down...")

app = FastAPI(title="LINE RAG Agent", lifespan=lifespan)

@app.get("/health")
def health(): return {"status": "ok"}

@app.post("/webhook")
async def webhook(request: Request): return await handle_line_webhook(request)

@app.post("/refresh")
def refresh(): return JSONResponse({"message": refresh_index()})
