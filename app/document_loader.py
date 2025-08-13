import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader

SUPPORTED_EXTS = {".txt", ".md", ".pdf"}

def load_documents(docs_dir: str):
    docs = []
    for root, _, files in os.walk(docs_dir):
        for f in files:
            path = os.path.join(root, f)
            ext = os.path.splitext(f)[1].lower()
            if ext not in SUPPORTED_EXTS: continue

            if ext == ".pdf":
                pages = PyPDFLoader(path).load()
                for d in pages:
                    d.metadata["source"] = path
                    d.metadata["page"] = d.metadata.get("page", 0) + 1
                docs.extend(pages)
            else:
                tdocs = TextLoader(path, encoding="utf-8").load()
                for d in tdocs:
                    d.metadata["source"] = path
                    d.metadata["page"] = 1
                docs.extend(tdocs)

    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    print(f"[ingest] files={len(docs)} chunks={len(chunks)}")
    return chunks
