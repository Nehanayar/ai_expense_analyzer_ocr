import streamlit as st
import pandas as pd
import plotly.express as px
import os, re, smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

from auth import login, register
from report import generate_pdf_report
from database import (
    create_tables, insert_default_categories,
    view_categories, add_category,
    add_expense, get_expenses, view_expense,
    delete_expense, update_expense,
    get_budget, set_budget,
)

load_dotenv()

# ── OCR ──────────────────────────────────────────────────────────────
try:
    from PIL import Image as PILImage
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# ── PAGE CONFIG ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Expense Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═════════════════════════════════════════════════════════════════════
# GLOBAL STYLES
# ═════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"]          { font-family: 'Inter', sans-serif; }
#MainMenu, footer                   { visibility: hidden; }
.stApp                              { background: #f8fafc; }

/* ── Sidebar ── */
[data-testid="stSidebar"]           { background: #ffffff !important; border-right: 1px solid #e2e8f0; display: block !important; visibility: visible !important; }
[data-testid="stSidebarNav"]        { display: block !important; }
section[data-testid="stSidebar"]    { min-width: 260px !important; }


/* ── Cards ── */
.card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 16px; padding: 24px 28px;
    margin-bottom: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

/* ── Section title ── */
.section-title {
    font-size: 22px; font-weight: 800; color: #111827;
    margin-bottom: 20px; padding-bottom: 10px;
    border-bottom: 3px solid #2563eb; display: inline-block;
}

/* ── Metric pills ── */
.metric-pill {
    background:#f0fdf4; border:1px solid #bbf7d0;
    border-radius:14px; padding:18px 16px; text-align:center;
}
.metric-pill .val { font-size:26px; font-weight:800; color:#16a34a; }
.metric-pill .lbl { font-size:11px; color:#6b7280; margin-top:3px; text-transform:uppercase; letter-spacing:.05em; }
.metric-pill.blue  { background:#eff6ff; border-color:#bfdbfe; }
.metric-pill.blue  .val { color:#2563eb; }
.metric-pill.amber { background:#fffbeb; border-color:#fde68a; }
.metric-pill.amber .val { color:#d97706; }
.metric-pill.red   { background:#fef2f2; border-color:#fecaca; }
.metric-pill.red   .val { color:#dc2626; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white; border: none; border-radius: 10px;
    padding: 10px 20px; font-weight: 600; font-size: 14px;
    width: 100%; transition: all .2s;
    box-shadow: 0 2px 6px rgba(37,99,235,.25);
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37,99,235,.35); }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput input {
    border-radius: 10px !important; border: 1.5px solid #e2e8f0 !important; font-size: 14px;
}

/* ── Badge ── */
.badge {
    display:inline-block; background:#dbeafe; color:#1d4ed8;
    font-size:11px; font-weight:700; padding:3px 10px; border-radius:20px;
}
.badge.green { background:#dcfce7; color:#15803d; }
.badge.red   { background:#fee2e2; color:#b91c1c; }
.badge.amber { background:#fef3c7; color:#92400e; }

/* ── Chat bubbles ── */
.chat-user {
    background:#eff6ff; border:1px solid #bfdbfe;
    padding:12px 16px; border-radius:12px 12px 4px 12px;
    margin-bottom:8px; color:#1e40af; font-size:14px;
}
.chat-bot {
    background:#f0fdf4; border:1px solid #bbf7d0;
    padding:12px 16px; border-radius:12px 12px 12px 4px;
    margin-bottom:8px; color:#166534; font-size:14px;
}

/* ── Landing ── */
.hero { text-align:center; padding:56px 20px 36px; }
.hero h1 { font-size:46px; font-weight:800; color:#111827; line-height:1.15; margin-bottom:14px; }
.hero p  { font-size:17px; color:#6b7280; max-width:540px; margin:0 auto 32px; }
.feature-grid {
    display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin:28px 0;
}
.feature-card {
    background:#fff; border:1px solid #e2e8f0; border-radius:14px;
    padding:22px 18px; text-align:center; box-shadow:0 1px 3px rgba(0,0,0,0.04);
}
.feature-card .icon { font-size:30px; margin-bottom:10px; }
.feature-card h3    { font-size:15px; font-weight:700; color:#111827; margin-bottom:5px; }
.feature-card p     { font-size:13px; color:#6b7280; margin:0; }

/* ── Sidebar stats ── */
.s-stat { background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:10px 14px; margin-bottom:7px; }
.s-stat .s-lbl { color:#9ca3af; font-size:10px; text-transform:uppercase; letter-spacing:.06em; }
.s-stat .s-val { color:#111827; font-weight:700; font-size:17px; }

/* ── OCR dashed box ── */
.ocr-box {
    background:#eff6ff; border:2px dashed #93c5fd;
    border-radius:14px; padding:24px; text-align:center; margin-bottom:16px;
}

/* ── Table tweaks ── */
[data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════
def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def send_email(to_email, subject, body):
    try:
        sender  = os.getenv("EMAIL_USER")
        passwd  = os.getenv("EMAIL_PASS")
        if not sender or not passwd:
            return
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"]    = sender
        msg["To"]      = to_email
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(sender, passwd)
            s.sendmail(sender, to_email, msg.as_string())
    except Exception:
        pass   # email is best-effort; don't break the app

def predict_category(text):
    """Call AI categorization — uses cached model from session."""
    ai_model      = st.session_state.get("ai_model")
    ai_embeddings = st.session_state.get("ai_embeddings")
    if ai_model is None or ai_embeddings is None:
        return "Uncategorized", 0.0
    text_emb = ai_model.encode(text.lower())
    scores = {}
    for cat, emb in ai_embeddings.items():
        denom = ((text_emb @ text_emb)**0.5) * ((emb @ emb)**0.5)
        scores[cat] = float((text_emb @ emb) / denom) if denom else 0.0
    best       = max(scores, key=scores.get)
    confidence = scores[best]
    return ("Uncategorized", confidence) if confidence < 0.28 else (best, confidence)

def extract_from_receipt(image):
    """Tesseract OCR → (amount, description)."""
    text   = pytesseract.image_to_string(image)
    lines  = [l.strip() for l in text.splitlines() if l.strip()]
    amount = None
    desc   = "Receipt expense"

    amount_re = re.compile(
        r'(?:rs\.?|inr|₹|total|amount|grand total)[^\d]*([\d,]+\.?\d*)', re.I
    )
    plain_re  = re.compile(r'\b(\d{2,6}(?:\.\d{1,2})?)\b')

    for line in lines:
        m = amount_re.search(line)
        if m:
            amount = float(m.group(1).replace(",", ""))
            break
    if amount is None:
        for line in lines:
            m = plain_re.search(line)
            if m:
                amount = float(m.group(1).replace(",", ""))
                break

    skip = {"total","amount","rs","inr","bill","invoice","receipt",
            "tax","gst","subtotal","cash","change","paid","thank","you"}
    for line in lines[:6]:
        words = line.lower().split()
        if not all(w in skip or w.replace(".","").replace(",","").isdigit() for w in words):
            desc = line
            break

    return amount, desc


# ═════════════════════════════════════════════════════════════════════
# INIT  (DB + AI model — load once)
# ═════════════════════════════════════════════════════════════════════
create_tables()
insert_default_categories()

if "ai_model" not in st.session_state:
    from sentence_transformers import SentenceTransformer
    with st.spinner("Loading AI model…"):
        m = SentenceTransformer("all-MiniLM-L6-v2")
    st.session_state.ai_model = m

    ai_categories = {
        "Food":          "pizza burger restaurant food swiggy zomato meals snacks lunch dinner",
        "Travel":        "uber ola taxi bus train transport travel cab flight petrol fuel",
        "Bills":         "electricity water rent internet recharge bills utility phone",
        "Shopping":      "amazon flipkart clothes shoes electronics shopping mall purchase",
        "Fitness":       "gym workout yoga sports health fitness protein supplement",
        "Insurance":     "LIC insurance health policy premium life insurance term",
        "Entertainment": "movie netflix hotstar spotify concert game fun entertainment",
        "Education":     "course book tuition college university school fees education",
        "Health":        "doctor hospital medicine pharmacy clinic checkup health",
        "Other":         "miscellaneous other general expense",
    }
    st.session_state.ai_embeddings = {
        cat: m.encode(text) for cat, text in ai_categories.items()
    }

if "user"         not in st.session_state: st.session_state.user         = None
if "alert_sent"   not in st.session_state: st.session_state.alert_sent   = False
if "chat_history" not in st.session_state: st.session_state.chat_history = []


# ═════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
        <div style='padding:14px 0 6px;'>
            <span style='font-size:22px;font-weight:800;color:#2563eb;'>💰 AI Expense Analyzer</span><br>
            <span style='font-size:11px;color:#9ca3af;'>Powered by SpendSmart</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if st.session_state.user:
        uid      = st.session_state.user[0]
        uname    = st.session_state.user[1]

        st.markdown(f"""
            <div style='background:#eff6ff;border-radius:10px;padding:10px 14px;margin-bottom:14px;'>
                <div style='font-size:11px;color:#6b7280;'>Logged in as</div>
                <div style='font-weight:700;color:#1d4ed8;font-size:15px;'>👤 {uname}</div>
            </div>
        """, unsafe_allow_html=True)

        # ── Live stats ────────────────────────────────────────────
        raw = view_expense(uid)
        if raw:
            dfs = pd.DataFrame(raw, columns=["Amount","Category","Date"])
            dfs["Date"] = pd.to_datetime(dfs["Date"])
            now         = pd.Timestamp.now()

            today_total = dfs[dfs["Date"].dt.date == now.date()]["Amount"].sum()
            month_total = dfs[
                (dfs["Date"].dt.month == now.month) &
                (dfs["Date"].dt.year  == now.year)
            ]["Amount"].sum()
            budget_val  = get_budget(uid)
            remaining   = budget_val - month_total

            st.markdown("**📊 Quick Stats**")
            st.markdown(f"""
                <div class='s-stat'>
                    <div class='s-lbl'>Today</div>
                    <div class='s-val'>₹{today_total:,.0f}</div>
                </div>
                <div class='s-stat'>
                    <div class='s-lbl'>This Month</div>
                    <div class='s-val'>₹{month_total:,.0f}</div>
                </div>
            """, unsafe_allow_html=True)

            if budget_val > 0:
                rc = "#16a34a" if remaining >= 0 else "#dc2626"
                rl = "Budget Left" if remaining >= 0 else "Over Budget"
                st.markdown(f"""
                    <div class='s-stat'>
                        <div class='s-lbl'>{rl}</div>
                        <div class='s-val' style='color:{rc};'>₹{abs(remaining):,.0f}</div>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("**🗂 Categories**")
            cats = dfs.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            mt   = dfs["Amount"].sum()
            for cat, amt in cats.items():
                pct = int(amt / mt * 100) if mt > 0 else 0
                st.markdown(f"""
                    <div style='display:flex;justify-content:space-between;align-items:center;
                                font-size:13px;padding:4px 0;border-bottom:1px solid #f1f5f9;'>
                        <span style='color:#374151;'>{cat}</span>
                        <span style='font-weight:600;color:#2563eb;'>
                            ₹{amt:,.0f}
                            <span style='color:#9ca3af;font-weight:400;'> {pct}%</span>
                        </span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("")

        st.markdown("---")
        page = st.radio(
            "Navigate",
            ["➕ Add Expense", "📋 View Expenses", "📊 Dashboard", "🤖 Chatbot"],
            key="main_nav",
        )
        st.markdown("")
        if st.button("🚪 Logout"):
            for k in ["user","alert_sent","chat_history"]:
                st.session_state[k] = None if k == "user" else False if k == "alert_sent" else []
            st.rerun()

    else:
        page = st.radio(
            "Navigate",
            ["🏠 Home", "🔐 Login", "📝 Register", "➕ Add Expense"],
            key="guest_nav",
        )
        st.markdown("---")
        st.caption("Sign in to track expenses, view analytics & get AI predictions.")


# ═════════════════════════════════════════════════════════════════════
# ─── NOT LOGGED IN ───────────────────────────────────────────────────
# ═════════════════════════════════════════════════════════════════════
if not st.session_state.user:

    # ── HOME / ADD EXPENSE (guest) ────────────────────────────────────
    if page in ("🏠 Home", "➕ Add Expense"):

        if page == "➕ Add Expense":
            st.info("📌 **Please login or register** to start tracking your expenses.")

        st.markdown("""
        <div class='hero'>
            <h1>AI Expense<br><span style='color:#2563eb;'>Analyzer</span></h1>
            <p>SpendSmart uses AI to automatically track, categorize, and predict
               your spending — so you always know where your money goes.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='feature-grid'>
            <div class='feature-card'>
                <div class='icon'>🤖</div>
                <h3>AI Categorization</h3>
                <p>Type any expense — AI instantly picks the right category.</p>
            </div>
            <div class='feature-card'>
                <div class='icon'>📸</div>
                <h3>Receipt OCR</h3>
                <p>Snap a bill photo — SpendSmart reads and logs it for you.</p>
            </div>
            <div class='feature-card'>
                <div class='icon'>📈</div>
                <h3>ML Predictions</h3>
                <p>See your predicted next-month spending before it happens.</p>
            </div>
            <div class='feature-card'>
                <div class='icon'>🎯</div>
                <h3>Budget Alerts</h3>
                <p>Set a limit and get an email alert when you're over budget.</p>
            </div>
            <div class='feature-card'>
                <div class='icon'>📄</div>
                <h3>PDF Reports</h3>
                <p>Download a professional expense report with charts anytime.</p>
            </div>
            <div class='feature-card'>
                <div class='icon'>💬</div>
                <h3>Expense Chatbot</h3>
                <p>Ask anything about your spending in plain language.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🚀 Get Started — It's Free"):
                # redirect hint — user clicks Register in sidebar
                st.info("👈 Click **Register** in the sidebar to create your account!")

    # ── LOGIN ─────────────────────────────────────────────────────────
    elif page == "🔐 Login":
        _, col, _ = st.columns([1, 1.2, 1])
        with col:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>🔐 Welcome back</div>", unsafe_allow_html=True)
            email = st.text_input("Email address", key="li_email")
            pwd   = st.text_input("Password", type="password", key="li_pwd")
            if st.button("Login →", key="li_btn"):
                if not email or not pwd:
                    st.warning("Please fill all fields ⚠️")
                else:
                    result = login(email, pwd)
                    if result:
                        st.session_state.user       = result
                        st.session_state.alert_sent = False
                        st.success("Login successful! 🎉")
                        st.rerun()
                    else:
                        st.error("Invalid email or password ❌")
            st.markdown("</div>", unsafe_allow_html=True)

    # ── REGISTER ─────────────────────────────────────────────────────
    elif page == "📝 Register":
        _, col, _ = st.columns([1, 1.2, 1])
        with col:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>📝 Create account</div>", unsafe_allow_html=True)
            uname = st.text_input("Username")
            email = st.text_input("Email address")
            pwd   = st.text_input("Password", type="password")
            if st.button("Create Account →"):
                if not is_valid_email(email):
                    st.error("Invalid email format ❌")
                elif not uname or not pwd or not email:
                    st.warning("Please fill all fields ⚠️")
                else:
                    r = register(uname, pwd, email)
                    if r == "Success":
                        st.success("Account created! Click **Login** in the sidebar ✅")
                    elif r == "Username Exists":
                        st.error("Username already taken ❌")
                    elif r == "Email Exists":
                        st.error("Email already registered ❌")
                    else:
                        st.error(r)
            st.markdown("</div>", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════
# ─── LOGGED IN ───────────────────────────────────────────────────────
# ═════════════════════════════════════════════════════════════════════
else:
    uid = st.session_state.user[0]

    # ══════════════════════════════════════════════════════════════════
    # ADD EXPENSE
    # ══════════════════════════════════════════════════════════════════
    if page == "➕ Add Expense":
        st.markdown("<div class='section-title'>➕ Add Expense</div>", unsafe_allow_html=True)

        tab_manual, tab_ocr = st.tabs(["✏️ Manual Entry", "📸 Scan Receipt (OCR)"])

        # ── MANUAL ────────────────────────────────────────────────────
        with tab_manual:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            desc   = st.text_input("What did you spend on?",
                                   placeholder="e.g. Swiggy dinner, Uber ride, Gym fee…")
            amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
            date   = st.date_input("Date")
            cats   = view_categories()

            ai_cat, ai_conf = None, 0.0
            if desc:
                ai_cat, ai_conf = predict_category(desc)
                pct      = round(ai_conf * 100, 1)
                cls      = "green" if ai_conf >= 0.5 else "amber" if ai_conf >= 0.35 else "red"
                st.markdown(
                    f"🤖 AI suggests: <span class='badge {cls}'>{ai_cat}</span> "
                    f"<span style='font-size:12px;color:#9ca3af;'>({pct}% confidence)</span>",
                    unsafe_allow_html=True
                )

            use_ai = st.checkbox("Use AI suggested category", value=True)

            c1, c2 = st.columns(2)
            with c1: selected_cat = st.selectbox("Category", cats)
            with c2: new_cat      = st.text_input("Or create new category")

            st.markdown("</div>", unsafe_allow_html=True)

            if st.button("Add Expense ✅"):
                if ai_cat and ai_cat != "Uncategorized" and use_ai:
                    final_cat = ai_cat
                elif new_cat.strip():
                    final_cat = new_cat.strip().title()
                    if final_cat not in cats:
                        add_category(final_cat)
                else:
                    final_cat = selected_cat

                if desc and amount > 0:
                    add_expense(uid, amount, final_cat, str(date))
                    st.success(f"✅ ₹{amount:,.2f} added under **{final_cat}**")
                    st.rerun()
                else:
                    st.warning("Please enter a description and amount > 0 ⚠️")

        # ── OCR ───────────────────────────────────────────────────────
        with tab_ocr:
            if not OCR_AVAILABLE:
                st.error(
                    "Tesseract not installed.\n\n"
                    "**Step 1** — Install Python packages:\n```\npip install pytesseract Pillow\n```\n\n"
                    "**Step 2** — Install Tesseract binary:\n"
                    "- Windows: https://github.com/UB-Mannheim/tesseract/wiki\n"
                    "- Mac: `brew install tesseract`\n"
                    "- Linux: `sudo apt install tesseract-ocr`"
                )
            else:
                st.markdown("""
                    <div class='ocr-box'>
                        <div style='font-size:32px;'>📸</div>
                        <div style='font-weight:700;color:#1d4ed8;margin:8px 0 4px;font-size:16px;'>
                            Upload a receipt photo</div>
                        <div style='font-size:13px;color:#6b7280;'>
                            JPG, PNG or WEBP — SpendSmart will extract the amount automatically</div>
                    </div>
                """, unsafe_allow_html=True)

                uploaded = st.file_uploader(
                    "Choose image", type=["jpg","jpeg","png","webp"],
                    label_visibility="collapsed"
                )
                if uploaded:
                    img = PILImage.open(uploaded)
                    col_img, col_form = st.columns([1, 1.4])

                    with col_img:
                        st.image(img, caption="Uploaded receipt", use_column_width=True)

                    with col_form:
                        with st.spinner("🔍 Reading receipt…"):
                            ocr_amt, ocr_desc = extract_from_receipt(img)

                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        st.markdown("**Extracted details — confirm or edit:**")

                        conf_desc = st.text_input("Description",
                                                   value=ocr_desc or "",
                                                   key="ocr_desc")
                        conf_amt  = st.number_input("Amount (₹)",
                                                    value=float(ocr_amt) if ocr_amt else 0.0,
                                                    min_value=0.0, key="ocr_amt")
                        ocr_date  = st.date_input("Date", key="ocr_date")
                        cats      = view_categories()

                        ai_cat2, _ = ("", 0.0)
                        if conf_desc:
                            ai_cat2, _ = predict_category(conf_desc)
                            st.markdown(
                                f"🤖 AI suggests: <span class='badge green'>{ai_cat2}</span>",
                                unsafe_allow_html=True
                            )

                        ocr_cat = st.selectbox("Category", cats, key="ocr_cat")
                        st.markdown("</div>", unsafe_allow_html=True)

                        if st.button("Save Receipt Expense ✅"):
                            final_cat = ai_cat2 if ai_cat2 and ai_cat2 != "Uncategorized" else ocr_cat
                            if conf_desc and conf_amt > 0:
                                add_expense(uid, conf_amt, final_cat, str(ocr_date))
                                st.success(f"✅ ₹{conf_amt:,.2f} added under **{final_cat}**")
                                st.rerun()
                            else:
                                st.warning("Amount must be > 0 ⚠️")

        # ── Recent ────────────────────────────────────────────────────
        st.markdown(
            "<div class='section-title' style='margin-top:28px;'>📌 Recent Expenses</div>",
            unsafe_allow_html=True
        )
        raw = view_expense(uid)
        if raw:
            df_r = pd.DataFrame(raw, columns=["Amount","Category","Date"])
            df_r["Amount"] = df_r["Amount"].apply(lambda x: f"₹{x:,.2f}")
            st.dataframe(df_r.head(5), use_container_width=True, hide_index=True)
        else:
            st.info("No expenses yet — add your first one above! 👆")


    # ══════════════════════════════════════════════════════════════════
    # VIEW EXPENSES
    # ══════════════════════════════════════════════════════════════════
    elif page == "📋 View Expenses":
        st.markdown("<div class='section-title'>📋 All Expenses</div>", unsafe_allow_html=True)

        raw = get_expenses(uid)
        if raw:
            df = pd.DataFrame(raw, columns=["ID","User","Amount","Category","Date"])

            # ── Filters ───────────────────────────────────────────────
            cf1, cf2 = st.columns(2)
            with cf1:
                cat_opts     = ["All"] + sorted(df["Category"].unique().tolist())
                filter_cat   = st.selectbox("Filter by category", cat_opts)
            with cf2:
                month_opts   = ["All"] + sorted(df["Date"].str[:7].unique().tolist(), reverse=True)
                filter_month = st.selectbox("Filter by month (YYYY-MM)", month_opts)

            dv = df.copy()
            if filter_cat   != "All": dv = dv[dv["Category"] == filter_cat]
            if filter_month != "All": dv = dv[dv["Date"].str.startswith(filter_month)]

            st.dataframe(
                dv[["Amount","Category","Date"]].assign(
                    Amount=dv["Amount"].apply(lambda x: f"₹{x:,.2f}")
                ).reset_index(drop=True),
                use_container_width=True, hide_index=True
            )
            st.caption(f"Showing {len(dv)} of {len(df)} expenses")

            st.markdown("---")

            # ── Edit / Delete ─────────────────────────────────────────
            col_ed, col_del = st.columns(2)
            options = {
                f"{r['Category']} — ₹{r['Amount']:,.2f} ({r['Date']})": r["ID"]
                for _, r in df.iterrows()
            }

            with col_del:
                st.markdown("**🗑 Delete expense**")
                sel_del = st.selectbox("Select to delete", list(options.keys()), key="sel_del")
                if st.button("Delete ❌"):
                    delete_expense(options[sel_del])
                    st.success("Deleted ✅")
                    st.rerun()

            with col_ed:
                st.markdown("**✏️ Edit expense**")
                sel_edit = st.selectbox("Select to edit", list(options.keys()), key="sel_edit")
                edit_id  = options[sel_edit]
                edit_row = df[df["ID"] == edit_id].iloc[0]

                new_amt  = st.number_input("New amount", value=float(edit_row["Amount"]),
                                           min_value=0.0, key="edit_amt")
                new_cat  = st.selectbox("New category", view_categories(),
                                        index=view_categories().index(edit_row["Category"])
                                        if edit_row["Category"] in view_categories() else 0,
                                        key="edit_cat")
                import datetime
                try:
                    default_date = datetime.date.fromisoformat(str(edit_row["Date"])[:10])
                except Exception:
                    default_date = datetime.date.today()
                new_date = st.date_input("New date", value=default_date, key="edit_date")

                if st.button("Save Changes ✅"):
                    update_expense(edit_id, new_amt, new_cat, str(new_date))
                    st.success("Updated ✅")
                    st.rerun()
        else:
            st.info("No expenses yet. Start by adding one! 💸")


    # ══════════════════════════════════════════════════════════════════
    # DASHBOARD
    # ══════════════════════════════════════════════════════════════════
    elif page == "📊 Dashboard":
        st.markdown("<div class='section-title'>📊 Dashboard</div>", unsafe_allow_html=True)

        raw = get_expenses(uid)
        if raw:
            df = pd.DataFrame(raw, columns=["ID","User","Amount","Category","Date"])
            df["Date"] = pd.to_datetime(df["Date"])

            from model import load_model as lm, train_model, predict_next_month

            model = lm()
            if model is None:
                model = train_model(df)

            # ── Budget ────────────────────────────────────────────────
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("**🎯 Monthly Budget**")
            db_budget = get_budget(uid)
            if "budget" not in st.session_state:
                st.session_state.budget = db_budget
            budget_input = st.number_input(
                "Set your monthly budget (₹)",
                value=float(st.session_state.budget),
                min_value=0.0, step=500.0, key="budget_input"
            )
            if st.button("Save Budget"):
                set_budget(uid, budget_input)
                st.session_state.budget     = budget_input
                st.session_state.alert_sent = False
                st.success("Budget saved ✅")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            # ── Calculations ──────────────────────────────────────────
            total      = df["Amount"].sum()
            now        = pd.Timestamp.now()
            this_month = df[(df["Date"].dt.month == now.month) &
                            (df["Date"].dt.year  == now.year)]
            month_tot  = this_month["Amount"].sum()
            cat_sum    = df.groupby("Category")["Amount"].sum()
            most_spent = cat_sum.idxmax()
            budget_val = st.session_state.budget

            monthly_check = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
            if len(monthly_check) < 3:
                ml_pred, lower, upper, insight = 0, 0, 0, "Need 3+ months of data for prediction"
            else:
                ml_pred, lower, upper, insight = predict_next_month(model, df)

            # ── Metric pills ──────────────────────────────────────────
            over = budget_val > 0 and month_tot > budget_val
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='metric-pill blue'><div class='val'>₹{total:,.0f}</div><div class='lbl'>All-time Total</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-pill amber'><div class='val'>₹{budget_val:,.0f}</div><div class='lbl'>Monthly Budget</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='metric-pill {'red' if over else ''}'><div class='val'>₹{month_tot:,.0f}</div><div class='lbl'>This Month</div></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='metric-pill'><div class='val'>₹{ml_pred:,.0f}</div><div class='lbl'>Next Month (ML)</div></div>", unsafe_allow_html=True)
            st.markdown("")

            if over:
                st.error(f"⚠️ Over budget by ₹{month_tot - budget_val:,.2f}")
            elif budget_val > 0:
                st.success(f"✅ Within budget — ₹{budget_val - month_tot:,.2f} remaining")

            # ── Charts ────────────────────────────────────────────────
            cl, cr = st.columns(2)
            with cl:
                fig = px.pie(values=cat_sum.values, names=cat_sum.index,
                             hole=0.42, title="Spending by Category",
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(margin=dict(t=40,b=10,l=10,r=10), height=310)
                st.plotly_chart(fig, use_container_width=True)

            with cr:
                fig = px.line(df.sort_values("Date"), x="Date", y="Amount",
                              title="Spending Over Time",
                              color_discrete_sequence=["#2563eb"])
                fig.update_traces(line=dict(width=2.5))
                fig.update_layout(margin=dict(t=40,b=10,l=10,r=10), height=310)
                st.plotly_chart(fig, use_container_width=True)

            monthly = df.groupby(df["Date"].dt.to_period("M"))["Amount"].sum()
            monthly.index = monthly.index.astype(str)
            fig = px.bar(x=monthly.index, y=monthly.values,
                         title="Monthly Spending",
                         labels={"x":"Month","y":"₹"},
                         color_discrete_sequence=["#2563eb"])
            fig.update_layout(margin=dict(t=40,b=10,l=10,r=10), height=300)
            st.plotly_chart(fig, use_container_width=True)

            # ── AI Insight ────────────────────────────────────────────
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("### 🧠 AI Insight")
            if ml_pred > 0:
                st.write(f"**Next month prediction:** ₹{ml_pred:,.2f}")
                st.info(f"📊 Expected range: ₹{lower:,.0f} – ₹{upper:,.0f}")
                st.success(insight)
                if budget_val > 0:
                    if ml_pred > budget_val:
                        st.error(f"⚠️ ML predicts you'll exceed budget by ₹{ml_pred - budget_val:,.0f}")
                    else:
                        st.success(f"✅ ML predicts you'll stay within budget")
                st.warning(f"⚡ You spend most on **{most_spent}** — consider reducing it")
            else:
                st.info("Add expenses for 3+ months to unlock ML predictions.")
            st.markdown("</div>", unsafe_allow_html=True)

            # ── Email alert (once per login session) ──────────────────
            user_email = st.session_state.user[3]
            status_msg = (
                f"{'⚠️ Over budget' if over else '✅ Within budget'} — "
                f"₹{month_tot:,.0f} spent of ₹{budget_val:,.0f} budget"
            )
            if not st.session_state.alert_sent:
                send_email(
                    user_email,
                    "📊 SpendSmart Monthly Report",
                    f"{status_msg}\n\nTop category: {most_spent}\nML prediction: ₹{ml_pred:,.0f}"
                )
                st.session_state.alert_sent = True

            # ── PDF ───────────────────────────────────────────────────
            st.markdown("---")
            st.markdown("**📄 Download Report**")
            st.caption("Full expense report with charts and ML prediction")
            if st.button("⬇️ Generate PDF Report"):
                with st.spinner("Building your report…"):
                    path = generate_pdf_report(st.session_state.user, df, total, ml_pred)
                with open(path, "rb") as f:
                    st.download_button(
                        "📥 Download PDF", f,
                        file_name="SpendSmart_Report.pdf",
                        mime="application/pdf"
                    )
        else:
            st.info("No expenses yet. Head to **➕ Add Expense** to get started! 💸")


    # ══════════════════════════════════════════════════════════════════
    # CHATBOT
    # ══════════════════════════════════════════════════════════════════
    elif page == "🤖 Chatbot":
        st.markdown("<div class='section-title'>🤖 Expense Chatbot</div>", unsafe_allow_html=True)

        raw = view_expense(uid)
        if raw:
            df = pd.DataFrame(raw, columns=["Amount","Category","Date"])
            df["Date"] = pd.to_datetime(df["Date"])

            col_chat, col_help = st.columns([2.5, 1])

            with col_help:
                st.markdown("""
                    <div class='card'>
                        <div style='font-weight:700;color:#374151;margin-bottom:10px;'>💡 Try asking</div>
                        <div style='font-size:13px;color:#6b7280;line-height:2.2;'>
                            What is my total expense?<br>
                            Average spending per transaction?<br>
                            Which category I spend most?<br>
                            How much this month?<br>
                            What was my last expense?<br>
                            How much on food?
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with col_chat:
                if st.button("🧹 Clear chat"):
                    st.session_state.chat_history = []
                    st.rerun()

                user_input = st.text_input("Ask about your expenses…", key="chat_inp")

                if st.button("Send 💬") and user_input:
                    from sentence_transformers import util as st_util

                    ai_model = st.session_state.ai_model
                    intents  = {
                        "total":    ai_model.encode("total expense how much spent overall"),
                        "average":  ai_model.encode("average spending per transaction mean"),
                        "most":     ai_model.encode("highest spending category most expensive"),
                        "month":    ai_model.encode("this month current month spending"),
                        "recent":   ai_model.encode("last latest recent expense"),
                        "category": ai_model.encode("category specific food travel bills shopping"),
                    }
                    q_emb  = ai_model.encode(user_input)
                    scores = {k: st_util.cos_sim(q_emb, v).item() for k, v in intents.items()}
                    best   = max(scores, key=scores.get)

                    now    = pd.Timestamp.now()
                    month_df = df[(df["Date"].dt.month == now.month) &
                                  (df["Date"].dt.year  == now.year)]

                    # Check for specific category name in query
                    cats_in_data = df["Category"].unique()
                    matched_cat  = next(
                        (c for c in cats_in_data if c.lower() in user_input.lower()), None
                    )

                    if matched_cat:
                        cat_total = df[df["Category"] == matched_cat]["Amount"].sum()
                        response  = f"🏷 **{matched_cat}**: ₹{cat_total:,.2f} total spent"
                    elif best == "total":
                        response = f"💰 Total expenses: **₹{df['Amount'].sum():,.2f}**"
                    elif best == "average":
                        response = f"📊 Average per transaction: **₹{df['Amount'].mean():,.2f}**"
                    elif best == "most":
                        top = df.groupby("Category")["Amount"].sum()
                        response = f"📈 Most spent on: **{top.idxmax()}** (₹{top.max():,.0f})"
                    elif best == "month":
                        response = f"📅 This month so far: **₹{month_df['Amount'].sum():,.2f}**"
                    elif best == "recent":
                        last = df.sort_values("Date").iloc[-1]
                        response = (f"🕐 Last expense: **{last['Category']}** — "
                                    f"₹{last['Amount']:,.0f} on {last['Date'].date()}")
                    else:
                        response = "🤔 I can answer about totals, categories, averages & recent expenses. Try rephrasing!"

                    st.session_state.chat_history.append(("You", user_input))
                    st.session_state.chat_history.append(("Bot", response))
                    st.rerun()

                for speaker, msg in reversed(st.session_state.chat_history):
                    css = "chat-user" if speaker == "You" else "chat-bot"
                    lbl = "👤 You" if speaker == "You" else "🤖 SpendSmart"
                    st.markdown(
                        f"<div class='{css}'><b>{lbl}:</b> {msg}</div>",
                        unsafe_allow_html=True
                    )
        else:
            st.info("Add some expenses first, then come back and chat! 💬")
