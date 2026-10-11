
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_model():
    """Load the model once and reuse it."""
    return SentenceTransformer(MODEL_NAME)


def calculate_semantic_similarity(
    resume_text: str,
    job_description: str,
) -> float:
    """Calculate semantic similarity between two documents."""
    if not resume_text.strip() or not job_description.strip():
        raise ValueError("Resume and job description cannot be empty.")

    model = load_model()

    embeddings = model.encode(
        [resume_text, job_description],
        normalize_embeddings=True,
    )

    score = cosine_similarity(
        embeddings[0].reshape(1, -1),
        embeddings[1].reshape(1, -1),
    )[0][0]

    return round(float(score) * 100, 2)