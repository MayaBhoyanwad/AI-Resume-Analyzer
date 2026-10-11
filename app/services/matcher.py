
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.semantic_matcher import (
    calculate_semantic_similarity,
)


# Canonical skill names and their common variations.
SKILL_ALIASES = {
    "python": ["python", "python3"],
    "java": ["java"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "rest api": ["rest api", "rest apis", "restful api", "restful apis"],
    "api development": ["api development", "api design"],
    "sql": ["sql"],
    "postgresql": ["postgresql", "postgres"],
    "mysql": ["mysql"],
    "sqlite": ["sqlite"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "scikit learn", "sklearn"],
    "machine learning": ["machine learning"],
    "deep learning": ["deep learning"],
    "natural language processing": [
        "natural language processing",
        "nlp",
    ],
    "computer vision": ["computer vision"],
    "data analysis": ["data analysis", "data analytics"],
    "data visualization": ["data visualization"],
    "data cleaning": ["data cleaning", "data preprocessing"],
    "etl": ["etl", "extract transform load"],
    "data warehouse": ["data warehouse", "data warehousing"],
    "power bi": ["power bi", "powerbi"],
    "excel": ["excel", "microsoft excel"],
    "tableau": ["tableau"],
    "git": ["git"],
    "github": ["github"],
    "docker": ["docker"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure", "microsoft azure"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "javascript": ["javascript", "js"],
    "streamlit": ["streamlit"],
    "bootstrap": ["bootstrap"],
    "react": ["react", "react.js", "reactjs"],
    "rest api testing": ["api testing", "rest api testing"],
    "postman": ["postman"],
    "oop": ["oop", "object oriented programming"],
    "data structures": ["data structures"],
    "algorithms": ["algorithms", "algorithm design"],
    "problem solving": ["problem solving", "analytical thinking"],
    "debugging": ["debugging", "troubleshooting"],
    "authentication": ["authentication"],
    "authorization": ["authorization"],
    "crud": ["crud", "create read update delete"],
    "json": ["json"],
    "linux": ["linux"],
    "networking": ["networking", "computer networks"],
}


def normalize_text(text: str) -> str:
    """Normalize text before comparison."""
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def contains_term(text: str, term: str) -> bool:
    """Match a term without matching it inside unrelated words."""
    pattern = r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)"
    return bool(re.search(pattern, text))


def extract_skills(text: str) -> list[str]:
    """Extract canonical skill names, handling common aliases."""
    normalized = normalize_text(text)
    found_skills = []

    for canonical_skill, aliases in SKILL_ALIASES.items():
        if any(contains_term(normalized, alias) for alias in aliases):
            found_skills.append(canonical_skill)

    return sorted(set(found_skills))


def calculate_similarity(
    resume_text: str,
    job_description: str,
) -> float:
    """Calculate TF-IDF cosine similarity as a percentage."""
    if not normalize_text(resume_text) or not normalize_text(job_description):
        raise ValueError("Resume and job description cannot be empty.")

    vectorizer = TfidfVectorizer(stop_words="english")

    try:
        vectors = vectorizer.fit_transform(
            [resume_text, job_description]
        )
    except ValueError:
        # For example, both documents contain only stop words.
        return 0.0

    similarity = cosine_similarity(
        vectors[0],
        vectors[1],
    )[0][0]

    return round(float(similarity) * 100, 2)


def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Analyze resume relevance using text similarity and skill coverage.

    The overall score is a relevance indicator, not an official ATS
    score or a prediction of hiring success.
    """
    if not normalize_text(resume_text) or not normalize_text(job_description):
        raise ValueError("Resume and job description cannot be empty.")

    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))

    matched_skills = sorted(resume_skills & job_skills)
    missing_skills = sorted(job_skills - resume_skills)
    additional_skills = sorted(resume_skills - job_skills)

    # Percentage of detected job-description skills found in the resume.
    skill_match_score = round(
        len(matched_skills) / len(job_skills) * 100,
        2,
    ) if job_skills else 0.0

    keyword_similarity = calculate_similarity(
        resume_text,
        job_description,
    )

    semantic_similarity = float(
        calculate_semantic_similarity(
            resume_text,
            job_description,
        )
    )

    # Keep the existing weighting so the current dashboard remains
    # compatible. This is an experimental relevance score.
    overall_score = round(
        0.4 * keyword_similarity + 0.6 * semantic_similarity,
        2,
    )

    suggestions = []

    if missing_skills:
        suggestions.append(
            "Review these job-description skills: "
            + ", ".join(missing_skills)
            + ". Add them only if you genuinely have the skills or experience."
        )

    if keyword_similarity < 30:
        suggestions.append(
            "Use clear, relevant wording from the job description "
            "where it accurately describes your experience."
        )

    if not matched_skills:
        suggestions.append(
            "Highlight relevant projects, technical skills, and "
            "achievements that align with the target role."
        )

    if matched_skills and not missing_skills:
        suggestions.append(
            "All detected job-description skills were found. "
            "Strengthen your resume with specific project outcomes "
            "and measurable achievements."
        )

    if not suggestions:
        suggestions.append(
            "Highlight relevant project outcomes and measurable achievements."
        )

    return {
        # Existing keys: retained for compatibility with your UI.
        "overall_score": overall_score,
        "keyword_similarity": keyword_similarity,
        "semantic_similarity": round(semantic_similarity, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "suggestions": suggestions,

        # Additional fields for dashboard improvements.
        "skill_match_score": skill_match_score,
        "resume_skills": sorted(resume_skills),
        "job_skills": sorted(job_skills),
        "additional_skills": additional_skills,
        "matched_skill_count": len(matched_skills),
        "missing_skill_count": len(missing_skills),
        "total_job_skills": len(job_skills),
    }