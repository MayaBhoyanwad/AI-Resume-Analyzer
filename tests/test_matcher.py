from app.services.matcher import analyze_resume, extract_skills


def test_extract_skills():
    text = "I use Python, Django, PostgreSQL and Power BI."

    skills = extract_skills(text)

    assert "python" in skills
    assert "django" in skills
    assert "postgresql" in skills
    assert "power bi" in skills


def test_resume_matching():
    resume = """
    Python developer with Django, FastAPI, SQL and PostgreSQL.
    Built a customer sales analytics project using Pandas.
    """

    job = """
    Python developer required.
    Must know Python, Django, SQL, PostgreSQL and Docker.
    Experience with REST APIs is preferred.
    """

    result = analyze_resume(resume, job)

    assert 0 <= result["similarity_score"] <= 100
    assert "python" in result["matched_skills"]
    assert "docker" in result["missing_skills"]


def test_empty_resume_rejected():
    try:
        analyze_resume("", "Python developer with SQL")
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError for empty resume")


if __name__ == "__main__":
    test_extract_skills()
    test_resume_matching()
    test_empty_resume_rejected()

    print("All matching engine tests passed!")