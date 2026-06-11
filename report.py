import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ── COLOUR PALETTE ────────────────────────────────────────────────────
BLUE       = colors.HexColor("#2563eb")
LIGHT_BLUE = colors.HexColor("#eff6ff")
GREY_BG    = colors.HexColor("#f8fafc")
DARK_TEXT  = colors.HexColor("#111827")
MID_TEXT   = colors.HexColor("#6b7280")
GREEN      = colors.HexColor("#16a34a")
RED        = colors.HexColor("#dc2626")


def _make_styles():
    base = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=base["Normal"],
        fontSize=26,
        fontName="Helvetica-Bold",
        textColor=BLUE,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "ReportSub",
        parent=base["Normal"],
        fontSize=11,
        fontName="Helvetica",
        textColor=MID_TEXT,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=base["Normal"],
        fontSize=14,
        fontName="Helvetica-Bold",
        textColor=DARK_TEXT,
        spaceBefore=14,
        spaceAfter=6,
    )
    normal_style = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontSize=10,
        fontName="Helvetica",
        textColor=DARK_TEXT,
    )
    return title_style, sub_style, h2_style, normal_style


def generate_pdf_report(user, df, total, ml_prediction):
    name  = user[1]
    email = user[3]

    file_path = "SpendSmart_Report.pdf"
    doc = SimpleDocTemplate(
        file_path,
        rightMargin=40, leftMargin=40,
        topMargin=40,   bottomMargin=40,
    )

    title_style, sub_style, h2_style, normal_style = _make_styles()
    elements = []

    # ── HEADER ────────────────────────────────────────────────────────
    elements.append(Paragraph("💰 SpendSmart", title_style))
    elements.append(Paragraph("AI Expense Report", sub_style))
    elements.append(Spacer(1, 6))
    elements.append(HRFlowable(width="100%", thickness=2, color=BLUE))
    elements.append(Spacer(1, 10))

    # User info table
    user_data = [
        [Paragraph(f"<b>Name:</b> {name}",  normal_style),
         Paragraph(f"<b>Email:</b> {email}", normal_style)],
    ]
    user_table = Table(user_data, colWidths=[250, 250])
    user_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
        ("ROUNDEDCORNERS", [8]),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
    ]))
    elements.append(user_table)
    elements.append(Spacer(1, 16))

    # ── SUMMARY METRICS ───────────────────────────────────────────────
    elements.append(Paragraph("Summary", h2_style))

    summary_data = [
        ["Metric", "Value"],
        ["Total Expenses",     f"₹{total:,.2f}"],
        ["Next Month (ML)",    f"₹{ml_prediction:,.2f}" if ml_prediction else "N/A"],
        ["Total Transactions", str(len(df))],
        ["Top Category",       str(df.groupby("Category")["Amount"].sum().idxmax())],
    ]
    summary_table = Table(summary_data, colWidths=[250, 250])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  11),
        ("BACKGROUND",    (0, 1), (-1, -1), GREY_BG),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, GREY_BG]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 16))

    # ── RECENT EXPENSES TABLE ─────────────────────────────────────────
    elements.append(Paragraph("Recent Expenses (Last 10)", h2_style))

    df_recent  = df.tail(10)
    table_data = [["Date", "Category", "Amount"]]
    for _, row in df_recent.iterrows():
        table_data.append([
            str(row["Date"].date()) if hasattr(row["Date"], "date") else str(row["Date"]),
            row["Category"],
            f"₹{row['Amount']:,.2f}",
        ])

    exp_table = Table(table_data, colWidths=[140, 190, 170])
    exp_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  BLUE),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, GREY_BG]),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("ALIGN",         (2, 0), (2, -1),  "RIGHT"),
    ]))
    elements.append(exp_table)
    elements.append(Spacer(1, 20))

    # ── CHARTS ────────────────────────────────────────────────────────
    elements.append(Paragraph("Expense Charts", h2_style))

    cat_sum = df.groupby("Category")["Amount"].sum()

    # Pie chart
    pie_path = "report_pie.png"
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    wedge_colors = ["#2563eb","#7c3aed","#059669","#d97706","#dc2626",
                    "#0891b2","#65a30d","#db2777","#ea580c","#6366f1"]
    ax.pie(cat_sum.values, labels=cat_sum.index, autopct="%1.1f%%",
           colors=wedge_colors[:len(cat_sum)], startangle=140,
           textprops={"fontsize": 8})
    ax.set_title("Spending by Category", fontsize=11, fontweight="bold", pad=10)
    plt.tight_layout()
    plt.savefig(pie_path, dpi=140, bbox_inches="tight")
    plt.close(fig)

    # Bar chart
    bar_path = "report_bar.png"
    df2 = df.copy()
    df2["Date"] = pd.to_datetime(df2["Date"]) if "Date" in df2.columns else df2["Date"]

    import pandas as pd
    df2["Date"] = pd.to_datetime(df2["Date"])
    monthly = df2.groupby(df2["Date"].dt.to_period("M"))["Amount"].sum()
    monthly.index = monthly.index.astype(str)

    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    bars = ax.bar(monthly.index, monthly.values, color="#2563eb", width=0.5, edgecolor="white")
    ax.set_title("Monthly Spending", fontsize=11, fontweight="bold")
    ax.set_xlabel("Month", fontsize=9)
    ax.set_ylabel("₹ Amount", fontsize=9)
    ax.tick_params(axis="x", rotation=30, labelsize=7)
    ax.tick_params(axis="y", labelsize=8)
    ax.grid(axis="y", alpha=0.3)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f"₹{bar.get_height():,.0f}", ha="center", va="bottom", fontsize=7)
    plt.tight_layout()
    plt.savefig(bar_path, dpi=140, bbox_inches="tight")
    plt.close(fig)

    pie_img = Image(pie_path, width=2.8*inch, height=2.2*inch)
    bar_img = Image(bar_path, width=2.8*inch, height=2.2*inch)

    chart_table = Table([[pie_img, bar_img]], colWidths=[3*inch, 3*inch])
    chart_table.setStyle(TableStyle([
        ("ALIGN",  (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(chart_table)
    elements.append(Spacer(1, 16))

    # ── FOOTER ────────────────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
    elements.append(Spacer(1, 6))

    from reportlab.lib.styles import ParagraphStyle
    footer_style = ParagraphStyle(
        "Footer", fontSize=8, fontName="Helvetica",
        textColor=MID_TEXT, alignment=TA_CENTER
    )
    elements.append(Paragraph("Generated by SpendSmart – AI Expense Analyzer", footer_style))

    # ── BUILD ─────────────────────────────────────────────────────────
    doc.build(elements)

    # Clean up temp chart images
    for p in [pie_path, bar_path]:
        if os.path.exists(p):
            try:
                os.remove(p)
            except Exception:
                pass

    return file_path
