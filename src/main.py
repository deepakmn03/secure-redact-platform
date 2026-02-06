import os
import shutil
import uuid
from typing import List

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Import the class we just verified
from redactor import PDFRedactionService

app = FastAPI(title="Redaction API")

# Allow CORS so your frontend (running on a different port) can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories for temporary storage
UPLOAD_DIR = "uploads"
PROCESSED_DIR = "processed"

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def cleanup_files(file_paths: List[str]):
    """
    Background task to delete files after the request is completed.
    This prevents the server from filling up with sensitive documents.
    """
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            print(f"Error deleting file {path}: {e}")


@app.post("/redact")
async def redact_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    words: str = Form(...)  # Accepts comma-separated string: "secret, hidden, confidential"
):
    """
    1. Uploads a PDF.
    2. Redacts the specified words.
    3. Returns the redacted PDF.
    4. Deletes input/output files from the server.
    """
    
    # Validation: Ensure it's a PDF
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Generate unique filenames to avoid collisions
    session_id = str(uuid.uuid4())
    input_filename = f"{session_id}_input.pdf"
    output_filename = f"{session_id}_redacted.pdf"

    input_path = os.path.join(UPLOAD_DIR, input_filename)
    output_path = os.path.join(PROCESSED_DIR, output_filename)

    try:
        # 1. Save the uploaded file to disk
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. Parse the words (comma separated -> list)
        words_list = [w.strip() for w in words.split(",") if w.strip()]
        
        if not words_list:
            raise HTTPException(status_code=400, detail="No words provided for redaction.")

        # 3. Call our Redaction Engine
        service = PDFRedactionService(input_path)
        service.redact(words_list, output_path)

        # 4. Schedule Cleanup (Runs AFTER response is sent)
        background_tasks.add_task(cleanup_files, [input_path, output_path])

        # 5. Return the file
        return FileResponse(
            output_path, 
            media_type="application/pdf", 
            filename=f"redacted_{file.filename}"
        )

    except Exception as e:
        # If something goes wrong, clean up immediately
        cleanup_files([input_path])
        raise HTTPException(status_code=500, detail=str(e))