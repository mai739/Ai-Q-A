# app/rag_agent.py
import os
from typing import Optional
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from app.config import PERSIST_DIR, DOCS_DIR, OLLAMA_CHAT_MODEL, OLLAMA_EMBED_MODEL
from app.document_loader import load_documents
from functools import lru_cache

import logging

# แยกคอลเลกชันตามชื่อโมเดลฝัง ป้องกันมิติชนกันเวลาเปลี่ยนโมเดล
COLLECTION = f"docs_{OLLAMA_EMBED_MODEL}".replace("-", "_")

QA_PROMPT = PromptTemplate.from_template(
"""คุณเป็นผู้ช่วย "อาจารย์" "นักศึกษา" และ "เจ้าหน้าที่"
สาขาวิชาวิศวกรรมศาสตร์ เมคคาทรอกนิกส์
ตอบคำถามภาษาไทย

หลักเกณฑ์การตอบ:
1. หากพบข้อมูลใน CONTEXT: ตอบจากข้อมูลนั้น
2. หากไม่พบข้อมูล แต่คุณรู้จากความรู้ทั่วไป: ตอบ + บอกว่า "ความเห็นจาก AI"
3. หากไม่แน่ใจ: ตอบว่า "ไม่พบในเอกสาร"

คำถาม: {question}
CONTEXT:
{context}

คำตอบ (สั้น กระชับ ชัดเจน):"""
)

_vectorstore: Optional[Chroma] = None
_qa: Optional[RetrievalQA] = None

def ingest_documents():  # โหลดเอกสารเข้า
    """โหลดเอกสารจาก DOCS_DIR -> ฝังด้วย embedding -> บันทึกลง Chroma"""
    global _vectorstore
    docs = load_documents(DOCS_DIR)
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)

    if os.path.exists(PERSIST_DIR):
        vs = Chroma(
            persist_directory=PERSIST_DIR,
            collection_name=COLLECTION,
            embedding_function=embeddings,
        )
        vs.add_documents(docs)  # persist จะทำอัตโนมัติ
        vs.persist()
        _vectorstore = vs
    else:
        _vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            persist_directory=PERSIST_DIR,
            collection_name=COLLECTION,
        )

def ensure_chain():
    """เตรียม vectorstore & QA chain ให้พร้อมใช้งาน"""
    global _vectorstore, _qa
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)

    if _vectorstore is None:
        if os.path.exists(PERSIST_DIR):
            _vectorstore = Chroma(
                persist_directory=PERSIST_DIR,
                collection_name=COLLECTION,
                embedding_function=embeddings,
            )
        else:
            ingest_documents()

    # Retriever: ใช้เวกเตอร์ + MMR ให้หลากหลายขึ้น
    retriever = _vectorstore.as_retriever(search_kwargs={"k": 6})
    retriever.search_type = "mmr"

    # LLM: ลด temperature เพื่อลดความ "เดา"
    llm = ChatOllama(model=OLLAMA_CHAT_MODEL, temperature=0.2)

    _qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": QA_PROMPT},
        return_source_documents=True,
    )
@lru_cache(maxsize=100)
def answer_query(query: str) -> str:
    logging.info(f"Query received: {query[:100]}...")
    try:
        if _qa is None:
            ensure_chain()
        out = _qa.invoke({"query": query})
        if isinstance(out, dict):
            ans = (out.get("result") or "").strip()
            srcs = out.get("source_documents") or []
            if not ans:
                return "ไม่พบในเอกสาร"

            refs, seen = [], set()
            for s in srcs[:3]:
                name = os.path.basename(s.metadata.get("source", "")) or "unknown"
                page = s.metadata.get("page")
                key = (name, page)
                if key in seen:
                    continue
                seen.add(key)
                refs.append(f"- {name} (หน้า {page})" if page else f"- {name}")
            if refs:
                ans += "\n\nอ้างอิงจาก:\n" + "\n".join(refs)
            return ans
        return str(out)
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {str(e)}"

def refresh_index() -> str:
    """รีโหลดเอกสารและสร้าง chain ใหม่"""
    ingest_documents()
    ensure_chain()
    return "รีเฟรชดัชนีเรียบร้อย (โหลดเอกสารใหม่สำเร็จ)"