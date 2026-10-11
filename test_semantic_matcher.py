
from app.services.semantic_matcher import (
    calculate_semantic_similarity,
)

resume = """
I develop backend applications, create web services,
and work with relational databases.
"""

job = """
We need a Python developer experienced in REST API
development and SQL database management.
"""

score = calculate_semantic_similarity(resume, job)

print(f"Semantic similarity: {score}%")

assert 0 <= score <= 100
print("Semantic matching test passed!")