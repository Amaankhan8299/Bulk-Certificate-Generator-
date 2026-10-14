from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from pathlib import Path
from datetime import date


BASE_DIR = Path(__file__).resolve().parent
CERTIFICATES_DIR = BASE_DIR / "certificates"


def generate_certificate(
    name: str,
    event_name: str,
    certificate_id: str
) -> str:
    CERTIFICATES_DIR.mkdir(exist_ok=True)
    file_path = CERTIFICATES_DIR / f"{certificate_id}.pdf"

    page_size = landscape(A4)
    width, height = page_size
    pdf = canvas.Canvas(str(file_path), pagesize=page_size)

    # Background
    pdf.setFillColor(colors.HexColor("#FDFBF7"))
    pdf.rect(0, 0, width, height, fill=1, stroke=0)

    # Outer Border (Gold)
    pdf.setStrokeColor(colors.HexColor("#B8860B"))
    pdf.setLineWidth(3)
    pdf.rect(
        1 * cm,
        1 * cm,
        width - 2 * cm,
        height - 2 * cm
    )

    # Inner Border (Thin Gold)
    pdf.setLineWidth(1)
    pdf.rect(
        1.3 * cm,
        1.3 * cm,
        width - 2.6 * cm,
        height - 2.6 * cm
    )

    # Header / Title
    pdf.setFillColor(colors.HexColor("#17365D"))
    pdf.setFont("Helvetica-Bold", 32)
    pdf.drawCentredString(
        width / 2,
        height - 4.2 * cm,
        "CERTIFICATE OF COMPLETION"
    )

    # Subtitle
    pdf.setFillColor(colors.HexColor("#475569"))
    pdf.setFont("Helvetica", 15)
    pdf.drawCentredString(
        width / 2,
        height - 5.8 * cm,
        "This certificate is proudly presented to"
    )

    # Recipient Name
    pdf.setFillColor(colors.HexColor("#B8860B"))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(
        width / 2,
        height - 7.8 * cm,
        name
    )

    # Accent underline beneath recipient name
    pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
    pdf.setLineWidth(1)
    pdf.line(
        width / 2 - 8 * cm,
        height - 8.5 * cm,
        width / 2 + 8 * cm,
        height - 8.5 * cm
    )

    # Event Description
    pdf.setFillColor(colors.HexColor("#334155"))
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        width / 2,
        height - 10.2 * cm,
        f"for successfully participating in {event_name}"
    )

    # Date line on the left
    issue_date_str = date.today().strftime("%B %d, %Y")
    pdf.setStrokeColor(colors.HexColor("#94A3B8"))
    pdf.setLineWidth(1)
    pdf.line(3.5 * cm, 4.6 * cm, 8.5 * cm, 4.6 * cm)

    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(colors.HexColor("#1E293B"))
    pdf.drawCentredString(6.0 * cm, 4.0 * cm, issue_date_str)

    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.drawCentredString(6.0 * cm, 3.4 * cm, "Date of Issue")

    # Signature line on the right
    pdf.line(width - 8.5 * cm, 4.6 * cm, width - 3.5 * cm, 4.6 * cm)

    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(colors.HexColor("#1E293B"))
    pdf.drawCentredString(width - 6.0 * cm, 4.0 * cm, "Program Coordinator")

    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.drawCentredString(width - 6.0 * cm, 3.4 * cm, "Authorized Signature")

    # Bottom Certificate ID and Verification Info
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.HexColor("#64748B"))
    pdf.drawCentredString(
        width / 2,
        2.0 * cm,
        f"Certificate ID: {certificate_id}   |   Issue Date: {date.today().strftime('%d-%m-%Y')}"
    )

    # Save PDF
    pdf.save()

    return str(file_path)


if __name__ == "__main__":
    path = generate_certificate(
        name="Aman Khan",
        event_name="Python Workshop",
        certificate_id="CERT-001"
    )

    print(f"Certificate generated: {path}")

