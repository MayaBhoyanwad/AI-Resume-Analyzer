import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import os
import tempfile

import streamlit as st

from app.services.matcher import analyze_resume
from app.services.report_generator import generate_pdf_report
from app.services.resume_parser import extract_resume_text


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
)


# --------------------------------------------------
# Styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .stApp,
    [data-testid="stAppViewContainer"] {
        background: #F4F7FC;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    html, body, [class*="st-"] {
        font-family: "Inter", "Segoe UI", sans-serif;
    }

    h1, h2, h3 {
        color: #172B4D;
        letter-spacing: -0.3px;
    }

    .hero-banner {
        background: linear-gradient(120deg, #14213D, #243B67);
        padding: 30px 32px;
        border-radius: 20px;
        margin-bottom: 30px;
        box-shadow: 0 8px 24px rgba(20, 33, 61, 0.12);
    }

    .hero-eyebrow {
        color: #A9C7FF !important;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 10px;
    }

    .hero-banner .main-title {
        color: #FFFFFF !important;
        font-size: 2.25rem;
        font-weight: 750;
        line-height: 1.2;
        margin-bottom: 10px;
    }

    .hero-banner .subtitle {
        color: #D5DFF0 !important;
        font-size: 1rem;
        line-height: 1.7;
        margin-bottom: 0;
    }

    [data-testid="stSidebar"] {
        background: #14213D !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stSidebar"] ol,
    [data-testid="stSidebar"] ul,
    [data-testid="stSidebar"] li {
        color: #F3F6FC !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
        color: #B9C7DD !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: #354664 !important;
    }

    [data-testid="stFileUploader"] {
        background: #FFFFFF;
        border: 1px solid #D8E1EE;
        border-radius: 14px;
        padding: 16px;
        width: 100%;
        box-sizing: border-box;
    }

    [data-testid="stFileUploader"] section {
        background: #FFFFFF;
        border: 1px dashed #A8B9D3;
        border-radius: 10px;
        padding: 16px;
        box-sizing: border-box;
    }

    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] small {
        color: #172B4D;
    }

    [data-testid="stFileUploader"] button {
        background: #2864DC !important;
        color: #FFFFFF !important;
        border: 1px solid #2864DC !important;
        border-radius: 8px !important;
        min-height: 40px;
        padding: 0 16px;
        white-space: nowrap;
    }

    [data-testid="stFileUploader"] button p,
    [data-testid="stFileUploader"] button span {
        color: #FFFFFF !important;
    }

    [data-testid="stTextArea"] textarea {
        background: #FFFFFF !important;
        border: 1px solid #D8E1EE !important;
        border-radius: 12px !important;
        color: #172B4D !important;
        -webkit-text-fill-color: #172B4D !important;
        line-height: 1.6;
        opacity: 1 !important;
        box-sizing: border-box;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: #3976E8 !important;
        box-shadow: 0 0 0 2px rgba(57, 118, 232, 0.12);
    }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E3EAF4;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 14px rgba(24, 46, 82, 0.04);
    }

    [data-testid="stMetricLabel"] {
        color: #60718C !important;
        font-weight: 600;
    }

    [data-testid="stMetricValue"] {
        color: #2159C5 !important;
        font-size: 2rem;
        font-weight: 750;
    }

    .stButton > button,
    [data-testid="stDownloadButton"] > button {
        background: #2864DC !important;
        color: #FFFFFF !important;
        border: 1px solid #2864DC !important;
        border-radius: 10px !important;
        min-height: 46px;
        font-weight: 650;
        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    [data-testid="stDownloadButton"] > button:hover {
        background: #174CB4 !important;
        border-color: #174CB4 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(40, 100, 220, 0.2);
    }

    [data-testid="stProgressBar"] > div > div {
        background: #2864DC;
        border-radius: 10px;
    }

    hr {
        border-color: #DFE6F0;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 1rem;
        }

        .hero-banner {
            padding: 22px;
        }

        .hero-banner .main-title {
            font-size: 1.7rem;
        }

        [data-testid="stMetric"] {
            padding: 12px;
        }

        [data-testid="stFileUploader"] {
            padding: 10px;
        }
    }
   
/* Fix expander title overlapping with arrow */
[data-testid="stExpander"] summary {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    gap: 14px !important;
    padding: 14px 18px !important;
    min-height: 58px !important;
    box-sizing: border-box !important;
}

[data-testid="stExpander"] summary > div {
    flex: 1 1 auto !important;
    min-width: 0 !important;
}

[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] {
    min-width: 0 !important;
    overflow-wrap: anywhere !important;
}

[data-testid="stExpander"] summary svg {
    flex: 0 0 1rem !important;
    width: 1rem !important;
    height: 1rem !important;
    margin: 0 !important;
}

[data-testid="stExpander"] summary p {
    margin: 0 !important;
    line-height: 1.5 !important;
}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.title("📄 ResumeAI")
    st.caption("AI-powered resume analysis")
    st.divider()

    st.subheader("How it works")
    st.markdown(
        """
        1. Upload your resume.
        2. Paste a job description.
        3. Review the match analysis.
        4. Explore skill gaps.
        5. Download your PDF report.
        """
    )

    st.divider()
    st.caption("Supports PDF and DOCX files.")
    st.caption("Similarity scores are not hiring probabilities.")


# --------------------------------------------------
# Main header
# --------------------------------------------------
st.markdown(
    """
    <div class="hero-banner">
        <div class="hero-eyebrow">SMART CAREER TOOLKIT</div>
        <div class="main-title">AI Resume Analyzer</div>
        <div class="subtitle">
            Turn your resume into actionable insights.
            Discover skill gaps, compare job requirements,
            and prepare a stronger application.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Input section
# --------------------------------------------------
st.markdown("## Prepare your analysis")
st.caption("Upload your resume and add the target job description.")

upload_col, description_col = st.columns(
    [1, 1.5],
    gap="large",
)

with upload_col:
    st.subheader("📄 Your resume")
    st.caption("Upload a PDF or Word document (.docx).")

    resume_file = st.file_uploader(
        "Choose your resume",
        type=["pdf", "docx"],
        help="Upload a text-based PDF or Word document.",
        key="resume_upload",
        label_visibility="visible",
    )

    if resume_file is not None:
        st.success(f"Uploaded: {resume_file.name}")

    st.caption(
        "Maximum upload size is controlled by your Streamlit configuration."
    )


with description_col:
    st.subheader("💼 Target job description")
    st.caption(
        "Include responsibilities, required skills, and qualifications."
    )

    job_description = st.text_area(
        "Paste the job description",
        height=230,
        placeholder=(
            "Example: We are looking for a Python Developer "
            "with experience in Python, Django, REST APIs, "
            "SQL, PostgreSQL, Git and problem solving..."
        ),
        key="job_description",
        label_visibility="collapsed",
    )


st.divider()

analyze_clicked = st.button(
    "🔍 Analyze Resume",
    type="primary",
    use_container_width=True,
    key="analyze_resume_button",
)


# --------------------------------------------------
# Resume analysis
# --------------------------------------------------
if analyze_clicked:

    if resume_file is None:
        st.warning("Please upload your resume first.")

    elif not job_description.strip():
        st.warning("Please enter a job description.")

    else:
        temp_path = None

        try:
            with st.spinner(
                "Extracting resume text and calculating similarity..."
            ):
                suffix = os.path.splitext(
                    resume_file.name
                )[1].lower()

                with tempfile.NamedTemporaryFile(
                    suffix=suffix,
                    delete=False,
                ) as temp_file:
                    temp_file.write(resume_file.getvalue())
                    temp_path = temp_file.name

                resume_text = extract_resume_text(temp_path)

                if not resume_text or not resume_text.strip():
                    raise ValueError(
                        "No readable text was found in the uploaded resume. "
                        "Please upload a text-based PDF or DOCX file."
                    )

                result = analyze_resume(
                    resume_text,
                    job_description,
                )

            # ------------------------------------------
            # Main dashboard
            # ------------------------------------------
            st.success("Analysis completed successfully!")
            st.header("📊 Advanced Resume Analysis")

            score_col, keyword_col, semantic_col = st.columns(3)

            score_col.metric(
                "Overall Match",
                f"{result['overall_score']}%",
            )

            keyword_col.metric(
                "Keyword Similarity",
                f"{result['keyword_similarity']}%",
            )

            semantic_col.metric(
                "Semantic Similarity",
                f"{result['semantic_similarity']}%",
            )

            overall_score = min(
                max(float(result["overall_score"]) / 100, 0.0),
                1.0,
            )

            st.progress(
                overall_score,
                text="Overall text relevance",
            )

            st.caption(
                "Similarity is an experimental relevance indicator, "
                "not an official ATS score or hiring probability."
            )

            # ------------------------------------------
            # Skill coverage overview
            # ------------------------------------------
            st.divider()
            st.subheader("🎯 Job Skill Coverage")

            matched_skills = result.get("matched_skills", [])
            missing_skills = result.get("missing_skills", [])
            additional_skills = result.get("additional_skills", [])
            total_job_skills = result.get(
                "total_job_skills",
                len(matched_skills) + len(missing_skills),
            )

            skill_match_score = float(
                result.get("skill_match_score", 0)
            )

            coverage_col, matched_count_col, missing_count_col = (
                st.columns(3)
            )

            coverage_col.metric(
                "Skill Match",
                f"{skill_match_score:.2f}%",
            )

            matched_count_col.metric(
                "Matched Skills",
                result.get(
                    "matched_skill_count",
                    len(matched_skills),
                ),
            )

            missing_count_col.metric(
                "Skills to Review",
                result.get(
                    "missing_skill_count",
                    len(missing_skills),
                ),
            )

            st.progress(
                min(max(skill_match_score / 100, 0.0), 1.0),
                text=(
                    f"Matched {len(matched_skills)} of "
                    f"{total_job_skills} detected job skills"
                ),
            )

            if total_job_skills == 0:
                st.info(
                    "No tracked skills were detected in the job description. "
                    "Try including specific technical skills."
                )

            # ------------------------------------------
            # Matching and missing skills
            # ------------------------------------------
            st.divider()

            matched_col, missing_col = st.columns(
                2,
                gap="large",
            )

            with matched_col:
                st.subheader("✅ Matching Skills")

                if matched_skills:
                    for skill in matched_skills:
                        st.markdown(f"- 🟢 **{skill}**")
                else:
                    st.info(
                        "No matching tracked skills were detected."
                    )

            with missing_col:
                st.subheader("🔎 Skills to Review")

                if missing_skills:
                    for skill in missing_skills:
                        st.markdown(f"- 🟠 **{skill}**")

                    st.caption(
                        "Add a skill to your resume only if you genuinely "
                        "have that skill or relevant experience."
                    )
                else:
                    st.success(
                        "No missing tracked skills were detected."
                    )

          
            # ------------------------------------------
            # Improvement suggestions
            # ------------------------------------------
            st.divider()
            st.subheader("📝 Improvement Suggestions")

            suggestions = result.get("suggestions", [])

            if suggestions:
                for suggestion in suggestions:
                    st.markdown(f"- {suggestion}")
            else:
                st.info(
                    "No improvement suggestions are available."
                )

            # ------------------------------------------
            # PDF report
            # ------------------------------------------
            st.divider()
            st.subheader("📥 Download your report")

            pdf_bytes = generate_pdf_report(
                resume_file.name,
                result,
            )

            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_bytes,
                file_name="resume_analysis_report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key="download_pdf_report",
            )

            # ------------------------------------------
            # Extracted resume preview
            # ------------------------------------------
            st.divider()
            st.subheader("📄 Preview Extracted Resume Text")

            st.caption(
                "Review the text extracted from your uploaded document."
            )

            st.text_area(
                "Extracted resume text",
                value=resume_text,
                height=250,
                disabled=True,
                label_visibility="collapsed",
                key="extracted_resume_preview",
            )

        except (ValueError, OSError) as exc:
            st.error(f"Could not analyze the resume: {exc}")

        except Exception as exc:
            st.error(f"An unexpected error occurred: {exc}")

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass