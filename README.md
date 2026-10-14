# Bulk Certificate Generator 🎓

A fast, lightweight, and modern web application to generate personalized, verified PDF certificates in bulk.

## 🚀 Key Features

- **Bulk Generation:** Generate up to 100 certificates in a single batch.
- **Instant ZIP Download:** Download all generated certificates in one click as a ZIP bundle or individually.
- **Smart Validation:** Validates required fields, email formatting, max limits, and prevents duplicate recipient emails.
- **Paste & Import CSV:** Quick paste panel to populate multiple recipients instantly from CSV, TSV, or spreadsheet tables.
- **Elegant PDF Layout:** Generated with ReportLab in A4 Landscape, featuring dual gold borders, verification ID, and signature lines.
- **Interactive UI:** Clean, responsive, modern interface built with Vanilla CSS and modern JavaScript.

---

## 🛠️ Installation & Setup

### 1. Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Start the Application Server
```powershell
uvicorn main:app --reload
```

The app will be available at:
👉 **http://127.0.0.1:8000**

Interactive API Docs:
👉 **http://127.0.0.1:8000/docs**

---

## 🧪 Running Automated Tests

Run the test suite to verify model validations, boundary checks, PDF generation, security checks, and API endpoints:

```powershell
python test_validation.py
```

---

## 📁 Project Structure

```
Bulk Certificate Generator/
├── certificates/             # Generated PDF files
├── frontend/                 # Client UI
│   ├── index.html            # Main UI page
│   ├── script.js             # Client interactivity & API calls
│   └── style.css             # Modern styling & design tokens
├── certificate_generator.py  # ReportLab PDF generation logic
├── main.py                   # FastAPI backend server
├── requirements.txt          # Python dependencies
├── test_data.json            # Sample dataset (101 recipients)
└── test_validation.py        # Automated test suite
```
