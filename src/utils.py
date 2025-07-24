import os
from pathlib import Path
from fastapi import UploadFile
from typing import Optional
import shutil
from pdfminer.high_level import extract_text
from docx import Document
from pdfminer.layout import LAParams
from pdfminer.high_level import extract_text as pdf_extract_text

UPLOAD_FOLDER = "app/uploads"

def save_uploaded_file(file: UploadFile) -> str:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(str(UPLOAD_FOLDER), str(file.filename))

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path

def extract_text_from_file(file_path: str, file_type: str) -> Optional[str]:
    """
    Extract text from file while preserving paragraph structure
    
    Args:
        file_path: Path to the file
        file_type: File extension (pdf, docx)
    
    Returns:
        String with preserved paragraphs or None if extraction fails
    """
    try:
        if file_type == "pdf":
            return extract_text_from_pdf(file_path)
        elif file_type == "docx":
            return extract_text_from_docx(file_path)
        else:
            return None
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF with paragraph preservation
    
    Uses PDFMiner's layout analysis to detect paragraph breaks
    """
    laparams = LAParams(
        line_margin=0.5,  # Adjust to detect paragraph breaks
        word_margin=0.1,
        boxes_flow=0.5
    )
    
    raw_text = pdf_extract_text(file_path, laparams=laparams)
    
    # Post-processing to clean up paragraph breaks
    paragraphs = []
    current_para = []
    
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped:  # Empty line indicates paragraph break
            if current_para:  # Only add if we have content
                paragraphs.append(" ".join(current_para))
                current_para = []
        else:
            current_para.append(stripped)
    
    # Add the last paragraph if exists
    if current_para:
        paragraphs.append(" ".join(current_para))
    
    # Join paragraphs with double newlines (standard paragraph separation)
    return "\n\n".join(paragraphs)

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from DOCX with original paragraph structure
    """
    doc = Document(file_path)
    paragraphs = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:  # Only include non-empty paragraphs
            paragraphs.append(text)
    
    return "\n\n".join(paragraphs)
    
def get_file_type(filename: str):
    return Path(filename).suffix[1:].lower()