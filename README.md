# 💰 SpendSmart — AI Expense Analyzer

A full-stack AI-powered expense tracker built with Streamlit, Prophet ML, Tesseract OCR, and SQLite.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 AI Categorization | SentenceTransformer automatically detects expense category |
| 📸 Receipt OCR | Upload a bill photo — Tesseract reads the amount |
| 📈 ML Prediction | Prophet model predicts next month's spending |
| 🎯 Budget Alerts | Set a monthly budget, get email alerts |
| 📄 PDF Reports | Download professional report with charts |
| 💬 Chatbot | Ask questions about your spending in plain language |
| 🔒 Secure Auth | bcrypt password hashing, email+username validation |
| ✏️ Edit Expenses | Update any past expense |

---

## 🚀 Setup

### 1. Clone / download this folder

### 2. Create virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

### 3. Install Python packages
```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR binary

| OS | Command |
|---|---|
| Windows | Download from https://github.com/UB-Mannheim/tesseract/wiki |
| Mac | `brew install tesseract` |
| Linux | `sudo apt install tesseract-ocr` |

### 5. Set up email credentials
```bash
# Copy the example file
cp .env.example .env
# Edit .env and fill in your Gmail + App Password
```

To get a Gmail App Password:
1. Go to https://myaccount.google.com/apppasswords
2. Create a new app password
3. Paste it in `.env` as `EMAIL_PASS`

### 6. Run the app
```bash
streamlit run main.py
```

Open http://localhost:8501 in your browser.

---

## 📁 Project Structure

```
spendsmart/
├── main.py          ← Streamlit UI (all pages)
├── auth.py          ← Register / Login with bcrypt
├── database.py      ← SQLite CRUD operations
├── model.py         ← Prophet ML model
├── report.py        ← PDF report generation
├── requirements.txt ← Python dependencies
├── .env             ← Your email credentials (never share!)
└── .env.example     ← Template for .env
```

---

## 🗒 Notes

- The SQLite database (`expense.db`) is auto-created on first run.
- The Prophet model (`prophet_model.pkl`) is auto-trained once you have 3+ months of data.
- Keep `.env` out of Git — add it to `.gitignore`.
- Email sending is best-effort; if it fails the app still works.

---

## 🛠 Tech Stack

- **Frontend:** Streamlit + custom CSS (Inter font)
- **AI:** SentenceTransformers (`all-MiniLM-L6-v2`)
- **ML:** Facebook Prophet (time-series forecasting)
- **OCR:** Tesseract via pytesseract
- **DB:** SQLite3
- **Auth:** bcrypt
- **PDF:** ReportLab + Matplotlib
- **Charts:** Plotly Express
