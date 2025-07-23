import os
from pathlib import Path
from fastapi import UploadFile
from typing import Optional
import shutil
from pdfminer.high_level import extract_text
from docx import Document

UPLOAD_FOLDER = "app/uploads"

def save_uploaded_file(file: UploadFile) -> str:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(str(UPLOAD_FOLDER), str(file.filename))

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path

def extract_text_from_file(file_path:str, file_tipe:str) -> Optional[str]:
    try:
        if file_tipe == "pdf":
            return extract_text(file_path)
        elif file_tipe == "docx":
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return None
    except Exception as e:
        print(f"Error extracting text from file: {e}")
        return None
    
def get_file_type(filename: str):
    return Path(filename).suffix[1:].lower()