
from pathlib import Path

import pymupdf
from docx import Document


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF resume."""
    text_parts = []

    with pymupdf.open(file_path) as pdf:
        for page in pdf:
            text_parts.append(page.get_text())

    return "\n".join(text_parts).strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX resume."""
    document = Document(file_path)

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def extract_resume_text(file_path: str) -> str:
    """Extract text from a supported resume file."""
    path = Path(file_path)
    extension = path.suffix.lower()

    if not path.is_file():
        raise FileNotFoundError(f"Resume file not found: {file_path}")

    if extension == ".pdf":
        text = extract_text_from_pdf(str(path))
    elif extension == ".docx":
        text = extract_text_from_docx(str(path))
    else:
        raise ValueError("Unsupported format. Please upload a PDF or DOCX.")

    if not text:
        raise ValueError(
            "No text found. The resume may be scanned or image-based."
        )

    return text