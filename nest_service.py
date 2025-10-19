from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
import tempfile, os

app = FastAPI(title="Mythos Nest", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

NEST_DATA = []

@app.get("/health")
def health():
    return {"status": "nest-ok", "docs_indexed": len(NEST_DATA)}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    reader = PdfReader(tmp_path)
    text = " ".join(page.extract_text() or "" for page in reader.pages)
    chunks = [text[i:i+800] for i in range(0, len(text), 800)]
    for chunk in chunks:
        NEST_DATA.append({"source": file.filename, "chunk": chunk})
    os.remove(tmp_path)
    return {"file": file.filename, "chunks_added": len(chunks)}

@app.post("/search")
async def search(query: str):
    q = query.lower()
    results = [i for i in NEST_DATA if q in i["chunk"].lower()]
    return {"matches": results[:3]}
