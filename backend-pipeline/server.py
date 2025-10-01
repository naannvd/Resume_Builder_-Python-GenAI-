from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os, shutil, sys

sys.path.append(os.path.dirname(__file__))
from deepSeek import parse_resume_with_openrouter
from resume_exporter import export_resume_to_pdf

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ Mount uploads so they are publicly accessible
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
async def root():
    return {"message": "✅ FastAPI server is running"}

@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        parsed = parse_resume_with_openrouter(file_path, retry_fix=True)
        pdf_path = os.path.join(UPLOAD_DIR, file.filename.replace(".pdf", "_formatted.pdf"))
        export_resume_to_pdf(parsed, pdf_path)
    except Exception as e:
        return {"error": str(e)}

    # ✅ Return a public URL for frontend to load in iframe
    pdf_url = f"http://127.0.0.1:8000/uploads/{os.path.basename(pdf_path)}"
    return {"filename": file.filename, "parsed": parsed, "pdf_url": pdf_url}
