import io
import re
import uuid
import zipfile
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from certificate_generator import generate_certificate


BASE_DIR = Path(__file__).resolve().parent
CERTIFICATES_DIR = BASE_DIR / "certificates"
CERTIFICATES_DIR.mkdir(exist_ok=True)
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Bulk Certificate Generator API",
    description="Generate and download bulk PDF certificates with ease.",
    version="1.1.0"
)

# Allow all origins for seamless local dev & Live Server usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "certificates_count": len(list(CERTIFICATES_DIR.glob("*.pdf")))
    }



# Ek recipient ka data validate karna
class Recipient(BaseModel):
    name: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value


# Puri certificate request validate karna
class CertificateRequest(BaseModel):
    event_name: str
    recipients: List[Recipient] = Field(
        min_length=1,
        max_length=100
    )

    @field_validator("event_name")
    @classmethod
    def validate_event_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Event name cannot be empty")
        return value

    @model_validator(mode="after")
    def check_duplicate_emails(self):
        emails = [
            recipient.email.lower()
            for recipient in self.recipients
        ]

        if len(emails) != len(set(emails)):
            raise ValueError(
                "Duplicate email addresses are not allowed"
            )

        return self


# Har recipient ke liye PDF certificate generate karna
@app.post("/api/certificates")
def create_certificates(request: CertificateRequest):
    generated_files = []

    for recipient in request.recipients:
        certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"

        file_path = generate_certificate(
            name=recipient.name,
            event_name=request.event_name,
            certificate_id=certificate_id
        )

        generated_files.append({
            "name": recipient.name,
            "certificate_id": certificate_id,
            "file_path": str(file_path)
        })

    return {
        "message": "Certificates generated successfully",
        "event_name": request.event_name,
        "total_recipients": len(request.recipients),
        "certificates": generated_files
    }


# Ek certificate download karna
@app.get("/api/certificates/{certificate_id}/download")
def download_certificate(certificate_id: str):
    # Prevent path traversal attacks
    if not re.match(r"^[A-Za-z0-9_-]+$", certificate_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid certificate ID format"
        )

    file_path = (CERTIFICATES_DIR / f"{certificate_id}.pdf").resolve()

    # Ensure the resolved path is inside CERTIFICATES_DIR
    try:
        file_path.relative_to(CERTIFICATES_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden"
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=f"{certificate_id}.pdf"
    )


# Generated certificates ek ZIP mein download karna
@app.get("/api/certificates/download-zip")
def download_certificates_zip(ids: Optional[str] = Query(None, description="Comma-separated certificate IDs to include in the ZIP")):
    if ids:
        requested_ids = [i.strip() for i in ids.split(",") if i.strip()]
        pdf_files = []
        for cid in requested_ids:
            if re.match(r"^[A-Za-z0-9_-]+$", cid):
                p = (CERTIFICATES_DIR / f"{cid}.pdf").resolve()
                if p.is_file():
                    pdf_files.append(p)
    else:
        pdf_files = sorted(CERTIFICATES_DIR.glob("*.pdf"))

    if not pdf_files:
        raise HTTPException(
            status_code=404,
            detail="No certificates found to download"
        )

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED
    ) as zip_file:
        for pdf_file in pdf_files:
            zip_file.write(
                pdf_file,
                arcname=pdf_file.name
            )

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition":
                'attachment; filename="certificates.zip"'
        }
    )


# Mount frontend at root so index.html, style.css, and script.js work directly
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


