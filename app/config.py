import os
from dotenv import load_dotenv

load_dotenv()

CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")          # 🔧 ต้องตั้งค่า
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")  # 🔧 ต้องตั้งค่า

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

PERSIST_DIR = os.getenv("PERSIST_DIR", "./vectorstore")
DOCS_DIR = os.getenv("DOCS_DIR", "./data")

OLLAMA_CHAT_MODEL = os.getenv("OLLAMA_CHAT_MODEL", "gllama3.1:8b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "bge-m3")

if not CHANNEL_SECRET or not CHANNEL_ACCESS_TOKEN:
    raise RuntimeError("Missing LINE credentials. Set LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN in .env")