
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.services.matcher import analyze_resume
from app.services.resume_parser import extract_resume_text


app = FastAPI(
    title="AI Resume Analyzer",
    description="Analyze resume compatibility with a job description.",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "AI Resume Analyzer API is running!",
        "docs": "/docs",
    }


@app.post("/analyze")
async def analyze(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    filename = (resume.filename or "").lower()

    if not filename.endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF or DOCX resume.",
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty.",
        )

    suffix = Path(filename).suffix

    try:
        content = await resume.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded resume is empty.",
            )

        # Use a temporary file rather than retaining the upload.
        with NamedTemporaryFile(
            suffix=suffix, delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        try:
            resume_text = extract_resume_text(str(temp_path))
        finally:
            temp_path.unlink(missing_ok=True)

        result = analyze_resume(resume_text, job_description)

        return {
            "filename": resume.filename,
            "analysis": result,
        }

    except HTTPException:
        raise
    except (ValueError, OSError) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    finally:
        await resume.close()