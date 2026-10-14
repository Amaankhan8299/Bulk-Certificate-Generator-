import json
import os
import unittest
from pathlib import Path
from pydantic import ValidationError
from fastapi.testclient import TestClient

from main import app, CertificateRequest, Recipient
from certificate_generator import generate_certificate, CERTIFICATES_DIR


BASE_DIR = Path(__file__).resolve().parent
TEST_DATA_FILE = BASE_DIR / "test_data.json"


def ensure_test_data_json():
    """Generates test_data.json with 101 recipients for boundary testing."""
    data = {
        "event_name": "Python Workshop",
        "recipients": [
            {
                "name": f"Student {i}",
                "email": f"student{i}@example.com"
            }
            for i in range(1, 102)
        ]
    }
    with open(TEST_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


class TestBulkCertificateGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_test_data_json()
        cls.client = TestClient(app)

    def test_01_valid_request(self):
        """Test that valid request data passes Pydantic validation."""
        data = {
            "event_name": "AI & ML Bootcamp",
            "recipients": [
                {"name": "Alice Johnson", "email": "alice@example.com"},
                {"name": "Bob Smith", "email": "bob@example.com"}
            ]
        }
        req = CertificateRequest(**data)
        self.assertEqual(req.event_name, "AI & ML Bootcamp")
        self.assertEqual(len(req.recipients), 2)

    def test_02_empty_event_name(self):
        """Test that empty or whitespace event name raises ValidationError."""
        data = {
            "event_name": "   ",
            "recipients": [{"name": "Alice", "email": "alice@example.com"}]
        }
        with self.assertRaises(ValidationError) as ctx:
            CertificateRequest(**data)
        self.assertIn("Event name cannot be empty", str(ctx.exception))

    def test_03_empty_recipient_name(self):
        """Test that empty recipient name raises ValidationError."""
        data = {
            "event_name": "Workshop",
            "recipients": [{"name": "  ", "email": "alice@example.com"}]
        }
        with self.assertRaises(ValidationError) as ctx:
            CertificateRequest(**data)
        self.assertIn("Name cannot be empty", str(ctx.exception))

    def test_04_invalid_email(self):
        """Test that invalid email format raises ValidationError."""
        data = {
            "event_name": "Workshop",
            "recipients": [{"name": "Alice", "email": "not-an-email"}]
        }
        with self.assertRaises(ValidationError):
            CertificateRequest(**data)

    def test_05_duplicate_emails(self):
        """Test that duplicate emails (case-insensitive) raise ValidationError."""
        data = {
            "event_name": "Workshop",
            "recipients": [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "ALICE@EXAMPLE.COM"}
            ]
        }
        with self.assertRaises(ValidationError) as ctx:
            CertificateRequest(**data)
        self.assertIn("Duplicate email addresses are not allowed", str(ctx.exception))

    def test_06_max_100_recipients_limit(self):
        """Test that > 100 recipients raises ValidationError using test_data.json."""
        with open(TEST_DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data["recipients"]), 101)

        with self.assertRaises(ValidationError) as ctx:
            CertificateRequest(**data)
        errors = ctx.exception.errors()
        self.assertTrue(any("at most 100" in err.get("msg", "").lower() for err in errors))

    def test_07_pdf_generation(self):
        """Test that generate_certificate creates a valid PDF file."""
        test_id = "TEST-UNIT-001"
        file_path = generate_certificate(
            name="Unit Test User",
            event_name="Automated Testing",
            certificate_id=test_id
        )
        pdf_path = Path(file_path)
        self.assertTrue(pdf_path.is_file(), "Generated PDF file does not exist")
        self.assertGreater(pdf_path.stat().st_size, 500, "PDF file is too small")

    def test_08_api_home_and_health(self):
        """Test GET / and GET /api/health."""
        res_home = self.client.get("/")
        self.assertEqual(res_home.status_code, 200)

        res_health = self.client.get("/api/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.json()["status"], "healthy")

    def test_09_api_create_and_download(self):
        """Test POST /api/certificates and subsequent download."""
        payload = {
            "event_name": "API Test Event",
            "recipients": [
                {"name": "Integration User", "email": "integration@example.com"}
            ]
        }
        res = self.client.post("/api/certificates", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_recipients"], 1)

        cert_id = data["certificates"][0]["certificate_id"]

        # Test download endpoint
        dl_res = self.client.get(f"/api/certificates/{cert_id}/download")
        self.assertEqual(dl_res.status_code, 200)
        self.assertEqual(dl_res.headers["content-type"], "application/pdf")
        self.assertGreater(len(dl_res.content), 500)

        # Test ZIP download with specific id
        zip_res = self.client.get(f"/api/certificates/download-zip?ids={cert_id}")
        self.assertEqual(zip_res.status_code, 200)
        self.assertEqual(zip_res.headers["content-type"], "application/zip")
        self.assertGreater(len(zip_res.content), 500)

    def test_10_path_traversal_protection(self):
        """Test that directory traversal in certificate_id is blocked."""
        res = self.client.get("/api/certificates/..%2Fmain/download")
        self.assertIn(res.status_code, [400, 404])


if __name__ == "__main__":
    print("=" * 60)
    print("Running Bulk Certificate Generator Test Suite...")
    print("=" * 60)
    unittest.main(verbosity=2)