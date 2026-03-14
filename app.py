"""AUTX Agent: Document Reader

A file-capable AUTX agent that analyzes PDFs and images using OpenAI gpt-4o.
Accepts multipart uploads (prompt + files) and returns structured analysis.
"""

import base64
import io
import os

from fastapi import FastAPI, File, Form, Header, UploadFile
from openai import OpenAI
from PyPDF2 import PdfReader

app = FastAPI(title="AUTX Agent: Document Reader", version="1.0.0")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

SYSTEM_PROMPT = (
    "You are a document analysis assistant. Given text extracted from documents "
    "or images, answer the user's question accurately. Cite specific sections, "
    "numbers, or data points from the document. If the document content is "
    "unclear or insufficient, say so."
)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
PDF_EXTENSIONS = {".pdf"}


def extract_pdf_text(content: bytes) -> str:
    """Extract text from a PDF file."""
    reader = PdfReader(io.BytesIO(content))
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {i + 1}]\n{text}")
    return "\n\n".join(pages) if pages else "(No extractable text found in PDF)"


def get_extension(filename: str) -> str:
    """Get lowercase file extension."""
    return os.path.splitext(filename.lower())[1]


@app.post("/")
async def analyze(
    prompt: str = Form(...),
    files: list[UploadFile] = File(default=[]),
    x_autx_protocol: str | None = Header(default=None),
):
    """Analyze uploaded documents and answer the user's question."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    user_content = []
    files_processed = 0

    for f in files:
        content = await f.read()
        ext = get_extension(f.filename or "")
        files_processed += 1

        if ext in PDF_EXTENSIONS:
            text = extract_pdf_text(content)
            user_content.append({
                "type": "text",
                "text": f"Document '{f.filename}':\n{text}",
            })
        elif ext in IMAGE_EXTENSIONS:
            b64 = base64.b64encode(content).decode("utf-8")
            mime = f.content_type or "image/png"
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{mime};base64,{b64}"},
            })
        else:
            text = content.decode("utf-8", errors="replace")
            user_content.append({
                "type": "text",
                "text": f"File '{f.filename}':\n{text}",
            })

    user_content.append({"type": "text", "text": prompt})
    messages.append({"role": "user", "content": user_content})

    model = "gpt-4o" if any(
        get_extension(f.filename or "") in IMAGE_EXTENSIONS for f in files
    ) else "gpt-4o-mini"

    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1024,
        temperature=0.2,
    )

    return {
        "response": completion.choices[0].message.content or "",
        "files_processed": files_processed,
        "model": model,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/manifest")
async def manifest():
    """Return agent capabilities for AUTX discovery."""
    return {
        "input": {
            "type": "multipart",
            "accepts_files": True,
            "file_types": [".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".txt", ".csv"],
            "max_size_bytes": 20_000_000,
        },
        "output": {
            "type": "json",
            "produces_files": False,
            "content_types": ["application/json"],
            "max_size_bytes": 1_000_000,
        },
    }
