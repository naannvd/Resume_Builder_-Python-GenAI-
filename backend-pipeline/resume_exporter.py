from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from io import BytesIO

def export_resume_to_pdf(data, output_path: str = None):
    """
    Export resume as PDF.
    - If output_path is provided → saves to file.
    - If not → returns BytesIO object (for streaming to frontend).
    """

    buffer = BytesIO() if output_path is None else output_path
    doc = SimpleDocTemplate(buffer if isinstance(buffer, BytesIO) else output_path,
                            pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=40)

    styles = getSampleStyleSheet()

    # Custom styles
    name_style = ParagraphStyle("Name", parent=styles["Heading1"], fontSize=18, alignment=TA_LEFT, textColor=colors.black, spaceAfter=6)
    title_style = ParagraphStyle("Title", parent=styles["Normal"], fontSize=12, alignment=TA_LEFT, textColor=colors.HexColor("#E85C41"), spaceAfter=12)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#E85C41"), spaceBefore=12, spaceAfter=6)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14, alignment=TA_LEFT)

    story = []

    # Full Name
    story.append(Paragraph(f"<b>{data.get('full_name', '')}</b>", name_style))
    # Professional Title
    if data.get("title"):
        story.append(Paragraph(data.get("title", ""), title_style))
    story.append(Spacer(1, 12))

    # Career Highlights
    if data.get("summary"):
        story.append(Paragraph("Career Highlights", section_style))
        story.append(Paragraph(data.get("summary", ""), body_style))
        story.append(Spacer(1, 12))

    # Work Experience
    if data.get("experience"):
        story.append(Paragraph("Work Experience", section_style))
        for exp in data["experience"]:
            job_title = f"{exp.get('title', '')} – {exp.get('company', '')} ({exp.get('start_year', '')} – {exp.get('end_year', '')})"
            story.append(Paragraph(job_title, body_style))
            bullets = [ListItem(Paragraph(d, body_style)) for d in exp.get("description", [])]
            if bullets:
                story.append(ListFlowable(bullets, bulletType="bullet", leftIndent=20))
            story.append(Spacer(1, 6))

    # Projects
    if data.get("projects"):
        story.append(Paragraph("Projects", section_style))
        for proj in data["projects"]:
            story.append(Paragraph(f"<b>{proj.get('project_name', '')}</b>", body_style))
            bullets = [ListItem(Paragraph(d, body_style)) for d in proj.get("description", [])]
            if bullets:
                story.append(ListFlowable(bullets, bulletType="bullet", leftIndent=20))
            story.append(Spacer(1, 6))

    # Technical Skills
    if data.get("technical_skills"):
        story.append(Paragraph("Technical Skills", section_style))
        skills = ", ".join(data.get("technical_skills", []))
        story.append(Paragraph(skills, body_style))
        story.append(Spacer(1, 12))

    # Education
    if data.get("education"):
        story.append(Paragraph("Education", section_style))
        for edu in data["education"]:
            edu_text = f"{edu.get('degree', '')} – {edu.get('institution', '')}"
            story.append(Paragraph(edu_text, body_style))

    # Build PDF
    doc.build(story)

    if isinstance(buffer, BytesIO):
        buffer.seek(0)
        return buffer  # for API response
    else:
        print(f"✅ Resume exported to {output_path}")
        return output_path
