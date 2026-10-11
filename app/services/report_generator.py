
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf_report(filename: str, result: dict) -> bytes:
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=28,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#17365D"),
            spaceBefore=14,
            spaceAfter=7,
        )
    )

    story = []

    story.append(Paragraph("AI Resume Analyzer", styles["ReportTitle"]))
    story.append(
        Paragraph("Resume and Job Description Match Report", styles["Normal"])
    )
    story.append(Spacer(1, 18))

    story.append(Paragraph("Resume Details", styles["SectionHeading"]))
    story.append(
        Paragraph(f"<b>File:</b> {escape(filename)}", styles["Normal"])
    )
    story.append(Spacer(1, 12))

    score_data = [
        ["Metric", "Similarity Score"],
        ["Overall Match", f"{result['overall_score']}%"],
        ["Keyword Similarity", f"{result['keyword_similarity']}%"],
        ["Semantic Similarity", f"{result['semantic_similarity']}%"],
    ]

    score_table = Table(
        score_data,
        colWidths=[3.7 * inch, 2.0 * inch],
    )
    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F3F6FA")),
            ]
        )
    )

    story.append(Paragraph("Similarity Results", styles["SectionHeading"]))
    story.append(score_table)

    def add_list_section(heading, items, empty_message):
        story.append(Paragraph(heading, styles["SectionHeading"]))

        if items:
            for item in items:
                story.append(
                    Paragraph(f"- {escape(str(item))}", styles["Normal"])
                )
                story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(empty_message, styles["Normal"]))

    add_list_section(
        "Matching Skills",
        result["matched_skills"],
        "No matching skills were detected.",
    )

    add_list_section(
        "Skills to Review",
        result["missing_skills"],
        "No missing tracked skills were detected.",
    )

    add_list_section(
        "Improvement Suggestions",
        result["suggestions"],
        "No suggestions available.",
    )

    story.append(Spacer(1, 18))
    story.append(
        Paragraph(
            "<b>Important:</b> Similarity scores are experimental "
            "text comparisons. They do not represent a probability "
            "of being hired. Verify all skill recommendations against "
            "your actual experience.",
            styles["Italic"],
        )
    )

    document.build(story)
    return buffer.getvalue()