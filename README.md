# 💰 SpendSmart — AI Expense Analyzer

An end-to-end AI-powered personal finance tracker built using **Streamlit, Machine Learning (Prophet), OCR (Tesseract), NLP (SentenceTransformers), and SQLite**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 AI Categorization | Automatically classifies expenses using SentenceTransformer embeddings |
| 📸 Receipt OCR | Upload receipt images and extract text + amount using Tesseract |
| 📈 ML Forecasting | Prophet model predicts future monthly spending trends |
| 🎯 Budget Alerts | Set monthly budget and receive email notifications |
| 📄 PDF Reports | Download professional expense reports with charts |
| 💬 AI Chat Assistant | Ask questions about your spending in natural language |
| 🔒 Secure Authentication | bcrypt-based login system with validation |
| ✏️ Edit Expenses | Modify or update past transactions anytime |

---

## 🚀 Setup Instructions

### 1. Clone the project
```bash
git clone <your-repo-url>
cd spendsmart
2. Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Install Tesseract OCR
Windows: https://github.com/UB-Mannheim/tesseract/wiki
Mac: brew install tesseract
Linux: sudo apt install tesseract-ocr
5. Setup environment variables
cp .env.example .env

Edit .env:

EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password

Gmail App Password:
https://myaccount.google.com/apppasswords

6. Run the application
streamlit run main.py

Open in browser:

http://localhost:8501
📁 Project Structure
spendsmart/
│
├── main.py              # Streamlit UI
├── auth.py              # Authentication (bcrypt)
├── database.py          # SQLite operations
├── model.py             # Prophet forecasting model
├── report.py            # PDF report generator
├── requirements.txt
├── .env
├── .env.example
└── expense.db (auto-created)
🧠 How It Works (Technical Overview)
📊 Dataset
No external dataset is used
System builds a self-generated dataset
Data comes from user transactions stored in SQLite:
Date
Amount
Category
Description

👉 Over time, this becomes a personal financial intelligence dataset.

🤖 AI Categorization (Feature Extraction)

Model Used:

SentenceTransformer (all-MiniLM-L6-v2)

Working:

Converts text into vector embeddings
Compares similarity with category vectors
Assigns best matching category

Example:

Input: "Swiggy dinner order"
Output: Food 🍕
📸 OCR (Receipt Processing)

Library Used:

pytesseract (Tesseract OCR)

Workflow:

Upload receipt image
Image preprocessing using PIL
Text extraction using OCR
Parse amount + merchant details
📈 ML Model (Forecasting)

Model Used:

Facebook Prophet

Steps:

Convert data into time-series format
Train model on historical expenses
Predict future spending trends
📊 Feature Engineering

Extracted features:

Monthly total spending
Category-wise spending
Daily expense patterns
Transaction frequency
OCR extracted values
🗄️ Database (SQLite)
Column	Type
id	INTEGER PRIMARY KEY
date	TEXT
category	TEXT
amount	REAL
description	TEXT
📄 PDF Report Generation

Libraries Used:

ReportLab
Matplotlib

Includes:

Pie chart (expense distribution)
Bar chart (category-wise spending)
Clean professional layout


🔐 Authentication System
bcrypt password hashing
Email + username validation
Secure login/register system


💬 AI Chat Assistant
Rule-based assistant
Uses database queries
Answers questions like:
Total monthly spending
Highest category
Spending patterns


🛠️ Tech Stack
Frontend: Streamlit
Backend: Python
Database: SQLite
AI/NLP: SentenceTransformers
ML: Facebook Prophet
OCR: Tesseract
Visualization: Plotly + Matplotlib
PDF Generation: ReportLab
Security: bcrypt


🔥 Key Highlights
No external dataset required (self-learning system)
Combines AI + ML + OCR in one project
Learns from user behavior over time
Fully offline-capable (except email alerts)
Production-level project structure


🚀 Future Improvements
WhatsApp alerts integration
Bank transaction sync
Advanced LLM chatbot (ChatGPT-like assistant)
Cloud deployment (Streamlit Cloud / AWS)
Multi-user SaaS version
