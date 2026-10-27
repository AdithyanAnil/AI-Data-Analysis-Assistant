from io import BytesIO
from xml.sax.saxutils import escape

import pandas as pd
import plotly.io as pio

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
    Image,
    PageBreak
)

BRAND = colors.HexColor("#263B80")
ZEBRA = colors.HexColor("#F3F5FA")


def build_table(rows, col_widths, styles):
    """Build a full-width, left-aligned table with consistent styling."""
    cell_style = ParagraphStyle(
        "Cell", parent=styles["BodyText"], fontSize=10, leading=13
    )
    cell_right = ParagraphStyle("CellRight", parent=cell_style, alignment=2)
    head_style = ParagraphStyle(
        "Head", parent=cell_style,
        textColor=colors.white, fontName="Helvetica-Bold"
    )
    head_right = ParagraphStyle("HeadRight", parent=head_style, alignment=2)

    data = []
    for r, row in enumerate(rows):
        new_row = []
        for c, value in enumerate(row):
            text = escape(str(value))
            if r == 0:
                style = head_style if c == 0 else head_right
            else:
                style = cell_style if c == 0 else cell_right
            new_row.append(Paragraph(text, style))
        data.append(new_row)

    table = Table(data, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B0B6C3")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def create_pdf_report(df, profile, ai_insights, figures=None):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    full_width = doc.width            # usable width (~515pt on A4)
    col_widths = [full_width * 0.6, full_width * 0.4]

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=BRAND,
        fontSize=22,
        leading=28,
        spaceAfter=18
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        textColor=BRAND,
        spaceBefore=14,
        spaceAfter=8
    ))

    story = []

    story.append(Paragraph("AI Data Analysis Report", styles["ReportTitle"]))

    # ---- Dataset summary ----
    story.append(Paragraph("Dataset Summary", styles["SectionHeading"]))

    summary = [
        ["Metric", "Value"],
        ["Total rows", f"{len(df):,}"],
        ["Total columns", f"{len(df.columns):,}"],
        ["Missing cells", f"{int(df.isna().sum().sum()):,}"],
        ["Duplicate rows", f"{int(df.duplicated().sum()):,}"]
    ]
    story.append(build_table(summary, col_widths, styles))
    story.append(Spacer(1, 16))

    # ---- Data quality ----
    story.append(Paragraph("Data Quality", styles["SectionHeading"]))

    if profile["missing_values"]:
        rows = [["Column", "Missing values"]]
        rows += [[col, f"{count:,}"]
                 for col, count in profile["missing_values"].items()]
        story.append(build_table(rows, col_widths, styles))
    else:
        story.append(Paragraph("No missing values were found.",
                               styles["BodyText"]))

    # ---- Outliers ----
    story.append(Paragraph("Potential Outliers (IQR Method)",
                           styles["SectionHeading"]))

    outliers = profile["potential_outlier_counts_iqr"]
    if outliers:
        rows = [["Column", "Potential outliers"]]
        rows += [[col, f"{count:,}"] for col, count in outliers.items()]
        story.append(build_table(rows, col_widths, styles))
    else:
        story.append(Paragraph("No potential outliers were found.",
                               styles["BodyText"]))

    # ---- AI insights ----
    story.append(Paragraph("AI Analysis and Recommendations",
                           styles["SectionHeading"]))

    for line in ai_insights.splitlines():
        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
            continue

        if line.startswith("#"):
            heading = escape(line.lstrip("# ").strip())
            story.append(Paragraph(heading, styles["Heading3"]))
        else:
            story.append(Paragraph(escape(line), styles["BodyText"]))

    # ---- Charts ----
    if figures:
        story.append(PageBreak())
        story.append(Paragraph("Charts", styles["SectionHeading"]))

        for figure in figures:
            try:
                image_bytes = pio.to_image(
                    figure, format="png", width=1000, height=600
                )
                image_buffer = BytesIO(image_bytes)

                story.append(Image(
                    image_buffer,
                    width=full_width,
                    height=full_width * 0.6,   # keeps the 1000x600 ratio
                    hAlign="LEFT"
                ))
                story.append(Spacer(1, 15))

            except Exception:
                story.append(Paragraph(
                    "A chart could not be embedded in the PDF.",
                    styles["BodyText"]
                ))

    doc.build(story)

    return buffer.getvalue()