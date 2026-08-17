import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
import datetime


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="SmartCare AI | Clinical Intelligence",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# DESIGN SYSTEM — single-accent, calm clinical palette
# ==========================================================
# Instead of juggling navy + blue + teal, the whole UI now runs on ONE
# accent color (PRIMARY) plus neutrals. Color is reserved for meaning:
# the three RISK colors (green / amber / red) are the only other colors
# on screen, and they only ever appear where they actually communicate
# risk level.

BG = "#E9EDFB"          # light blue tint (derived from the accent color)
SURFACE = "#FFFFFF"     # card surface
SURFACE_2 = "#F3F5FD"   # subtle inset surface, softer blue than surface
BORDER = "#DCE2F5"      # thin card border

TEXT = "#1E1B39"        # near-black plum for headings
TEXT_2 = "#5B5876"      # secondary text
MUTED = "#9997B0"       # muted / labels

PRIMARY = "#6C63FF"     # single accent — indigo/violet
PRIMARY_DARK = "#4B3FD9"
PRIMARY_LIGHT = "#EDEBFF"

# Semantic-only colors (risk levels) — never used decoratively
LOW = "#1FAA6B"
MODERATE = "#E5A100"
HIGH = "#E23D5B"

RISK_COLORS = {
    "Low Risk": LOW,
    "Moderate Risk": MODERATE,
    "High Risk": HIGH,
}

# Kept for backward compatibility with earlier naming used below
NAVY = PRIMARY_DARK
BLUE = PRIMARY
TEAL = PRIMARY

# Sidebar gets its own darker blue treatment — kept separate from PRIMARY so
# the accent color (used for the active nav item, icons, etc.) still reads
# clearly against it instead of blending in.
SIDEBAR_BG = "#161C42"       # deep navy-blue
SIDEBAR_BORDER = "#272E5C"
SIDEBAR_TEXT = "#F1F2FC"     # near-white for headings/active items
SIDEBAR_MUTED = "#A6ABDE"    # soft lavender-blue for secondary text
SIDEBAR_HOVER_BG = "rgba(255,255,255,0.07)"


# ==========================================================
# CSS INJECTION
# ==========================================================

def inject_custom_css():
    """Injects all custom CSS for the SmartCare AI interface."""

    st.markdown(
        f"""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        :root {{
            --bg: {BG};
            --surface: {SURFACE};
            --surface2: {SURFACE_2};
            --border: {BORDER};
            --text: {TEXT};
            --text2: {TEXT_2};
            --muted: {MUTED};
            --primary: {PRIMARY};
            --primary-dark: {PRIMARY_DARK};
            --primary-light: {PRIMARY_LIGHT};
            --low: {LOW};
            --mod: {MODERATE};
            --high: {HIGH};
        }}

        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        .stApp {{
            background: var(--bg);
            color: var(--text);
            font-size: 1.04rem;
        }}

        .block-container {{
            max-width: 1360px;
            padding-top: 1.2rem;
            padding-bottom: 4rem;
        }}

        /* Hide Streamlit chrome */
        #MainMenu {{ visibility: hidden; }}
        footer {{ visibility: hidden; }}
        header {{ background: transparent !important; }}
        div[data-testid="stDecoration"] {{ display: none; }}

        h1, h2, h3 {{
            font-family: 'Poppins', sans-serif !important;
            color: var(--text) !important;
            letter-spacing: -0.01em;
        }}

        p, label, span {{ color: var(--text2); font-family: 'Poppins', sans-serif; }}

        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-thumb {{ background: #D6D5E8; border-radius: 8px; }}

        /* ---------------- Animations ---------------- */

        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}

        .anim {{ animation: fadeInUp 0.45s ease both; }}

        /* ---------------- Navbar ---------------- */

        .navbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 14px 22px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
            box-shadow: 0 6px 20px rgba(30,27,57,0.05);
            margin-bottom: 22px;
        }}

        .navbar-brand {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .navbar-logo {{
            width: 40px;
            height: 40px;
            border-radius: 12px;
            background: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            box-shadow: 0 6px 16px rgba(108,99,255,0.35);
        }}

        .navbar-title {{
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 1.18rem;
            color: var(--text);
            line-height: 1.1;
        }}

        .navbar-subtitle {{
            font-size: 0.76rem;
            color: var(--muted);
            font-weight: 600;
            letter-spacing: 0.04em;
        }}

        .navbar-status {{
            display: flex;
            align-items: center;
            gap: 7px;
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(31,170,107,0.09);
            border: 1px solid rgba(31,170,107,0.22);
            color: {LOW};
            font-size: 0.8rem;
            font-weight: 700;
        }}

        .pulse-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: {LOW};
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(31,170,107,0.45); }}
            70% {{ box-shadow: 0 0 0 7px rgba(31,170,107,0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(31,170,107,0); }}
        }}

        /* Nav tabs (st.radio used as pill nav) */

        div[role="radiogroup"] {{
            gap: 6px;
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 13px;
            padding: 6px;
        }}

        div[role="radiogroup"] label {{
            background: transparent !important;
            border-radius: 9px;
            padding: 8px 16px !important;
            font-weight: 600 !important;
            color: var(--text2) !important;
            transition: all 0.15s ease;
        }}

        div[role="radiogroup"] label:hover {{
            background: var(--primary-light) !important;
        }}

        /* ---------------- Nav buttons (Single Patient / Batch CSV) ---------------- */

        div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {{
            border-radius: 12px;
        }}

        /* ---------------- Sidebar ---------------- */

        section[data-testid="stSidebar"] {{
            background: {SIDEBAR_BG};
            border-right: 1px solid {SIDEBAR_BORDER};
        }}

        section[data-testid="stSidebar"] hr {{
            border-color: {SIDEBAR_BORDER};
        }}

        section[data-testid="stSidebar"] .stButton > button {{
            text-align: left;
            justify-content: flex-start;
            background: transparent;
            border: 1px solid transparent;
            color: {SIDEBAR_MUTED};
            font-weight: 600;
            min-height: 42px;
            box-shadow: none;
        }}

        section[data-testid="stSidebar"] .stButton > button:hover {{
            background: {SIDEBAR_HOVER_BG};
            color: {SIDEBAR_TEXT};
            transform: none;
            border-color: transparent;
        }}

        section[data-testid="stSidebar"] .st-key-nav_active button {{
            background: var(--primary) !important;
            color: #fff !important;
            box-shadow: 0 8px 18px rgba(108,99,255,0.45);
        }}

        section[data-testid="stSidebar"] .st-key-nav_active button:hover {{
            background: var(--primary-dark) !important;
            color: #fff !important;
        }}

        /* ---------------- Hero ---------------- */

        .hero {{
            position: relative;
            padding: 38px 40px;
            border: 1px solid var(--border);
            border-radius: 22px;
            background: var(--surface);
            box-shadow: 0 16px 45px rgba(30,27,57,0.05);
            margin-bottom: 22px;
            overflow: hidden;
        }}

        .hero::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 100% 0%, rgba(108,99,255,0.10), transparent 45%);
            pointer-events: none;
        }}

        .hero-badge {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 6px 13px;
            border-radius: 999px;
            background: var(--primary-light);
            border: 1px solid rgba(108,99,255,0.25);
            color: var(--primary-dark);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 16px;
            position: relative;
        }}

        .hero-title {{
            font-family: 'Poppins', sans-serif;
            font-size: clamp(1.95rem, 3.3vw, 2.85rem);
            font-weight: 700;
            line-height: 1.18;
            color: var(--text);
            margin-bottom: 14px;
            position: relative;
            max-width: 780px;
        }}

        .hero-title span {{
            color: var(--primary);
        }}

        .hero-description {{
            max-width: 660px;
            color: var(--text2);
            font-size: 1.06rem;
            line-height: 1.7;
            position: relative;
            margin-bottom: 22px;
        }}

        .hero-actions {{ display: flex; gap: 12px; position: relative; flex-wrap: wrap; }}

        .btn-primary, .btn-secondary {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 20px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.88rem;
            text-decoration: none;
            border: 1px solid transparent;
        }}

        .btn-primary {{
            background: var(--primary);
            color: #fff !important;
            box-shadow: 0 10px 24px rgba(108,99,255,0.30);
        }}

        .btn-secondary {{
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text) !important;
        }}

        /* ---------------- Section headers ---------------- */

        .section-eyebrow {{
            color: var(--primary);
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 6px;
        }}

        .section-title {{
            font-family: 'Poppins', sans-serif;
            color: var(--text);
            font-size: 1.6rem;
            font-weight: 700;
            margin-bottom: 4px;
        }}

        .section-desc {{
            color: var(--muted);
            font-size: 0.96rem;
            margin-bottom: 20px;
        }}

        /* ---------------- Metric / stat cards ---------------- */

        .metric-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 20px 20px;
            box-shadow: 0 8px 24px rgba(30,27,57,0.05);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            height: 100%;
        }}

        .metric-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 14px 30px rgba(30,27,57,0.10);
        }}

        .metric-icon {{
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.05rem;
            margin-bottom: 12px;
        }}

        .metric-value {{
            font-family: 'Poppins', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text);
            line-height: 1.1;
        }}

        .metric-label {{
            color: var(--muted);
            font-size: 0.84rem;
            font-weight: 600;
            margin-top: 4px;
        }}

        /* ---------------- Generic card ---------------- */

        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 22px;
            margin-bottom: 18px;
            box-shadow: 0 8px 24px rgba(30,27,57,0.045);
        }}

        .card-header {{
            display: flex;
            align-items: center;
            gap: 9px;
            color: var(--text);
            font-family: 'Poppins', sans-serif;
            font-size: 1.06rem;
            font-weight: 600;
            margin-bottom: 16px;
        }}

        .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            background: currentColor;
        }}

        /* Preset scenario cards */

        .preset-card {{
            min-height: 140px;
            padding: 16px;
            border-radius: 14px;
            background: var(--surface2);
            border: 1px solid var(--border);
            border-top: 3px solid var(--accent);
            transition: all 0.18s ease;
        }}

        .preset-card:hover {{
            transform: translateY(-3px);
            border-color: var(--accent);
            box-shadow: 0 10px 24px rgba(30,27,57,0.08);
        }}

        .preset-title {{
            color: var(--text);
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .preset-desc {{
            color: var(--muted);
            font-size: 0.79rem;
            line-height: 1.5;
        }}

        /* ---------------- Inputs (force white everywhere, all descendants) ---------------- */

        div[data-baseweb="base-input"],
        div[data-baseweb="input"],
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"],
        div[data-baseweb="select"] > div,
        div[data-baseweb="select"] div,
        div[data-testid="stNumberInput"] > div,
        div[data-testid="stNumberInput"] div,
        div[data-testid="stTextInput"] > div,
        div[data-testid="stTextInput"] div,
        textarea {{
            background-color: #FFFFFF !important;
            border-color: var(--border) !important;
            border-radius: 10px !important;
            color: var(--text) !important;
        }}

        input, textarea {{
            background-color: #FFFFFF !important;
            color: var(--text) !important;
            -webkit-text-fill-color: var(--text) !important;
            caret-color: var(--text) !important;
        }}

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div[role="button"] {{
            color: var(--text) !important;
        }}

        /* Number input +/- steppers */
        button[data-testid="stNumberInputStepUp"],
        button[data-testid="stNumberInputStepDown"] {{
            background-color: #FFFFFF !important;
            color: var(--text) !important;
            border-color: var(--border) !important;
        }}

        button[data-testid="stNumberInputStepUp"] svg,
        button[data-testid="stNumberInputStepDown"] svg {{
            fill: var(--text) !important;
        }}

        /* Selectbox dropdown popover / option list */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] div,
        ul[role="listbox"],
        li[role="option"] {{
            background-color: #FFFFFF !important;
            color: var(--text) !important;
        }}

        li[role="option"]:hover,
        li[role="option"][aria-selected="true"] {{
            background-color: var(--surface2) !important;
        }}

        /* Hide the hidden/readonly search input BaseWeb selects render internally —
           it can otherwise show up as a stray blank white box below the field. */
        div[data-baseweb="select"] input[readonly] {{
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            opacity: 0 !important;
        }}

        label {{
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            color: var(--text2) !important;
            font-family: 'Poppins', sans-serif !important;
        }}

        /* ---------------- Buttons ---------------- */

        .stButton > button {{
            width: 100%;
            border-radius: 12px;
            border: 1px solid rgba(108,99,255,0.28);
            background: var(--surface2);
            color: var(--text);
            font-weight: 600;
            font-size: 0.92rem;
            font-family: 'Poppins', sans-serif;
            min-height: 43px;
            transition: all 0.18s ease;
        }}

        .stButton > button:hover {{
            border-color: var(--primary);
            background: var(--primary-light);
            transform: translateY(-1px);
        }}

        /* Primary predict CTAs — targeted via st.button(key=...) */
        .st-key-predict_btn button,
        .st-key-run_batch_btn button {{
            background: var(--primary) !important;
            color: #fff !important;
            border: none !important;
            box-shadow: 0 10px 24px rgba(108,99,255,0.30);
        }}

        .st-key-predict_btn button:hover,
        .st-key-run_batch_btn button:hover {{
            background: var(--primary-dark) !important;
            transform: translateY(-1px);
        }}

        /* ---------------- Risk badge ---------------- */

        .risk-badge {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 8px 14px;
            border-radius: 999px;
            font-size: 0.88rem;
            font-weight: 700;
        }}

        /* ---------------- Chips ---------------- */

        .chip-row {{ display: flex; flex-wrap: wrap; gap: 8px; }}

        .chip {{
            padding: 9px 12px;
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--muted);
            font-size: 0.8rem;
        }}

        .chip b {{ color: var(--text); margin-left: 3px; }}

        /* ---------------- Risk scale ---------------- */

        .risk-scale {{
            position: relative;
            height: 10px;
            border-radius: 999px;
            background: linear-gradient(90deg, {LOW}, {MODERATE}, {HIGH});
            margin: 18px 0 8px 0;
        }}

        .risk-scale-marker {{
            position: absolute;
            top: -7px;
            width: 3px;
            height: 24px;
            background: var(--text);
            border-radius: 2px;
            transform: translateX(-50%);
        }}

        .risk-scale-labels {{
            display: flex;
            justify-content: space-between;
            font-size: 0.68rem;
            font-weight: 700;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}

        /* ---------------- Insight cards ---------------- */

        .insight-card {{
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px;
            height: 100%;
        }}

        .insight-title {{
            font-weight: 700;
            color: var(--text);
            font-size: 0.92rem;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 7px;
        }}

        .insight-text {{
            font-size: 0.84rem;
            color: var(--text2);
            line-height: 1.55;
        }}

        /* ---------------- Model info rows ---------------- */

        .info-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 11px 0;
            border-bottom: 1px solid var(--border);
        }}

        .info-row:last-child {{ border-bottom: none; }}

        .info-label {{
            color: var(--muted);
            font-size: 0.86rem;
            font-weight: 600;
        }}

        .info-value {{
            color: var(--text);
            font-size: 0.9rem;
            font-weight: 700;
        }}

        /* ---------------- Metrics (native) ---------------- */

        [data-testid="stMetric"] {{
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 13px;
            padding: 12px;
        }}

        [data-testid="stMetricLabel"] {{ color: var(--muted) !important; }}

        [data-testid="stMetricValue"] {{
            color: var(--text) !important;
            font-family: 'Poppins', sans-serif;
            font-size: 1.5rem !important;
        }}

        [data-testid="stMetricLabel"] {{
            font-family: 'Poppins', sans-serif !important;
            font-size: 0.85rem !important;
        }}

        /* ---------------- Dataframe ---------------- */

        [data-testid="stDataFrame"] {{
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid var(--border);
        }}

        /* ---------------- Download ---------------- */

        .stDownloadButton > button {{
            border-radius: 12px;
            background: var(--primary-light);
            border: 1px solid rgba(108,99,255,0.28);
            color: var(--primary-dark);
            font-weight: 700;
        }}

        /* ---------------- Alerts ---------------- */

        .stAlert {{ border-radius: 12px; border: 1px solid var(--border); }}

        /* ---------------- Divider ---------------- */

        .soft-divider {{ height: 1px; background: var(--border); margin: 18px 0; }}

        /* ---------------- Footer ---------------- */

        .footer {{
            text-align: center;
            color: var(--muted);
            font-size: 0.8rem;
            padding-top: 28px;
        }}

        .footer strong {{ color: var(--primary); }}

        /* ---------------- Responsive ---------------- */

        @media (max-width: 768px) {{
            .hero {{ padding: 26px 20px; }}
            .navbar {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# REQUIRED COLUMNS — every raw field the trained pipeline needs
# ==========================================================

REQUIRED_COLUMNS = [
    "patient_id", "age", "gender", "blood_group", "department", "diagnosis",
    "appointment_status", "admitted", "room_type", "length_of_stay_days",
    "previous_admissions", "systolic_bp", "diastolic_bp", "blood_sugar_mg_dl",
    "cholesterol_mg_dl", "bmi", "lab_tests_count", "treatments_count",
    "consultation_fee_lkr", "room_charge_lkr", "lab_charge_lkr",
    "medicine_charge_lkr", "waiting_days", "previous_appointments",
    "missed_previous_appointments", "appointment_date", "payment_status",
    "payment_method"
]


# ==========================================================
# TRAINED MODEL ARTIFACTS
# ==========================================================
# These are the exact files saved by Data_Understanding_Preprocessing.ipynb
# (Task 03) and Model_Development.ipynb (Task 05). Loading them here means
# this prototype scores patients with the same fitted Logistic Regression
# model, scaler, and encoding scheme that were evaluated in Model_Evaluation
# .ipynb — not a separately hand-written scoring rule.

MODEL_DIR_CANDIDATES = ["../models", "models", "./models"]

# Ordinal mappings must match Data_Understanding_Preprocessing.ipynb
# Section 3.9 exactly (bmi_category / bp_category encoding).
BMI_ORDER = {"Underweight": 0, "Normal": 1, "Overweight": 2, "Obese": 3}
BP_ORDER = {"Normal": 0, "Elevated": 1, "Hypertensive": 2}

# scikit-learn's .predict() (used throughout Model_Development.ipynb and
# Model_Evaluation.ipynb to report accuracy/precision/recall/F1) applies a
# default 0.5 cutoff to the predicted probability. The prototype uses the
# same cutoff so its Yes/No output matches the notebook's reported metrics.
DECISION_THRESHOLD = 0.50


@st.cache_resource(show_spinner=False)
def load_artifacts():
    """Loads the trained Logistic Regression model plus every preprocessing
    object needed to reproduce the notebook's feature pipeline exactly."""

    last_error = None

    for base in MODEL_DIR_CANDIDATES:
        try:
            model = joblib.load(os.path.join(base, "logistic_regression_model.pkl"))
            scaler = joblib.load(os.path.join(base, "scaler.pkl"))
            model_columns = joblib.load(os.path.join(base, "model_columns.pkl"))
            scaled_columns = joblib.load(os.path.join(base, "scaled_columns.pkl"))
            nominal_cols = joblib.load(os.path.join(base, "nominal_cols.pkl"))
            util_threshold = joblib.load(
                os.path.join(base, "high_utilisation_threshold.pkl")
            )

            return {
                "model": model,
                "scaler": scaler,
                "model_columns": model_columns,
                "scaled_columns": scaled_columns,
                "nominal_cols": nominal_cols,
                "high_utilisation_threshold": float(util_threshold),
                "base_dir": base,
            }

        except FileNotFoundError as error:
            last_error = error
            continue

    raise FileNotFoundError(
        "Could not find the trained model artifacts (logistic_regression_model.pkl, "
        "scaler.pkl, model_columns.pkl, scaled_columns.pkl, nominal_cols.pkl, "
        "high_utilisation_threshold.pkl). Run Data_Understanding_Preprocessing.ipynb "
        "and then Model_Development.ipynb from top to bottom so these files are saved "
        "under ../models/ (relative to the notebooks folder), then restart this app. "
        f"Looked in: {MODEL_DIR_CANDIDATES}. ({last_error})"
    )


# ==========================================================
# FEATURE ENGINEERING — mirrors Data_Understanding_Preprocessing.ipynb
# Section 3.7 exactly, including the appointment-date decomposition and
# the train-only high-utilisation threshold used by the trained model.
# ==========================================================

def preprocess_and_engineer_features(patient_dict):

    df = pd.DataFrame([patient_dict])

    appointment_date = pd.to_datetime(df["appointment_date"])
    df["appointment_month"] = appointment_date.dt.month
    df["appointment_dayofweek"] = appointment_date.dt.dayofweek
    df = df.drop(columns=["appointment_date"])

    df["total_bill_lkr"] = (
        df["consultation_fee_lkr"]
        + df["room_charge_lkr"]
        + df["lab_charge_lkr"]
        + df["medicine_charge_lkr"]
    )

    df["total_prior_visits"] = (
        df["previous_appointments"]
        + df["previous_admissions"]
    )

    df["missed_appointment_rate"] = np.where(
        df["previous_appointments"] > 0,
        df["missed_previous_appointments"]
        / df["previous_appointments"],
        0
    )

    def get_bmi_category(bmi):
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "Overweight"
        return "Obese"

    df["bmi_category"] = df["bmi"].apply(get_bmi_category)

    def get_bp_category(row):
        s = row["systolic_bp"]
        d = row["diastolic_bp"]

        if s < 120 and d < 80:
            return "Normal"
        elif s < 140 and d < 90:
            return "Elevated"
        return "Hypertensive"

    df["bp_category"] = df.apply(get_bp_category, axis=1)

    # Threshold learned from X_train only (see Section 5.9 / high_utilisation
    # in the report) — loaded from the saved artifact so the prototype uses
    # the identical cut point the model was trained and evaluated with.
    util_threshold = load_artifacts()["high_utilisation_threshold"]

    df["high_utilisation"] = (
        (df["lab_tests_count"] + df["treatments_count"]) >= util_threshold
    ).astype(int)

    df["avg_charge_per_treatment"] = (
        df["total_bill_lkr"]
        / (df["treatments_count"] + 1)
    )

    df["zero_room_charge_flag"] = (
        (df["length_of_stay_days"] > 0)
        & (df["room_charge_lkr"] == 0)
    ).astype(int)

    df["admission_status_conflict"] = (
        (df["admitted"] == 1)
        & (
            df["appointment_status"].isin(
                ["No-Show", "Cancelled"]
            )
        )
    ).astype(int)

    return df


# ==========================================================
# MODEL INPUT ALIGNMENT — reproduces Task 03's encoding/scaling so the
# feature vector fed to the model is bit-for-bit consistent with training
# ==========================================================

FRIENDLY_FEATURE_NAMES = {
    "admitted": "Inpatient Admission",
    "length_of_stay_days": "Length of Stay",
    "high_utilisation": "High Utilisation (Lab Tests + Treatments)",
    "admission_status_conflict": "Admission Status Conflict",
    "zero_room_charge_flag": "Zero Room Charge",
    "total_bill_lkr": "Total Bill",
    "age": "Age",
    "bmi_category": "BMI Category",
    "bp_category": "Blood Pressure Category",
    "total_prior_visits": "Prior Healthcare Visits",
    "missed_appointment_rate": "Missed-Appointment Rate",
    "avg_charge_per_treatment": "Average Charge per Treatment",
    "previous_admissions": "Previous Admissions",
    "waiting_days": "Waiting Days",
}


def _friendly_name(feature):
    if feature in FRIENDLY_FEATURE_NAMES:
        return FRIENDLY_FEATURE_NAMES[feature]
    # one-hot columns look like "room_type_ICU" -> "Room Type: ICU"
    for prefix in ["gender_", "blood_group_", "department_", "diagnosis_",
                   "appointment_status_", "room_type_", "payment_status_",
                   "payment_method_"]:
        if feature.startswith(prefix):
            base = prefix[:-1].replace("_", " ").title()
            value = feature[len(prefix):]
            return f"{base}: {value}"
    return feature.replace("_", " ").title()


def build_model_vector(engineered_df, artifacts):
    """Converts the human-readable engineered row into the exact numeric
    feature vector the trained Logistic Regression model expects:
    ordinal encoding for bmi_category/bp_category, one-hot encoding for
    the eight nominal columns aligned to the training-time dummy columns
    (an unseen/omitted category simply falls back to all-zeros, the same
    reference category pd.get_dummies(drop_first=True) drops at training
    time), and StandardScaler scaling for the continuous columns —
    mirroring Data_Understanding_Preprocessing.ipynb Sections 3.9-3.10.

    Column order is read from the fitted model's own
    `feature_names_in_` rather than the separately saved
    model_columns.pkl: in the notebook, high_utilisation is dropped
    before the train/test split and re-added afterwards (to fix the
    leakage issue flagged in the supervisor feedback), which shifts its
    position to the end of X_train — but model_columns.pkl was captured
    BEFORE that re-add, so it recorded the pre-leakage-fix column order.
    The two lists end up with the same 60 column names but in a
    different order, and scikit-learn matches columns by position, not
    by name, so using model_columns.pkl directly would silently score
    every patient with badly misaligned features. Using
    model.feature_names_in_ instead is always guaranteed to match what
    the model was actually fitted on. Consider re-saving
    model_columns.pkl as X_train.columns.tolist() (after the
    high_utilisation fix) in the notebook so the artifact is correct on
    its own terms too."""

    row = engineered_df.iloc[0]
    nominal_cols = artifacts["nominal_cols"]
    model_columns = list(artifacts["model"].feature_names_in_)

    numeric_row = {
        "bmi_category": BMI_ORDER.get(row["bmi_category"], 1),
        "bp_category": BP_ORDER.get(row["bp_category"], 0),
    }

    skip_cols = set(nominal_cols) | {"bmi_category", "bp_category"}
    for col, val in row.items():
        if col in skip_cols:
            continue
        numeric_row[col] = val

    for col in nominal_cols:
        value = str(row[col])
        for candidate in model_columns:
            if candidate.startswith(f"{col}_"):
                numeric_row.setdefault(candidate, 0)
        dummy_name = f"{col}_{value}"
        if dummy_name in model_columns:
            numeric_row[dummy_name] = 1

    X = pd.DataFrame([numeric_row])
    X = X.reindex(columns=model_columns, fill_value=0)

    scaler = artifacts["scaler"]
    scaled_columns = artifacts["scaled_columns"]
    X[scaled_columns] = scaler.transform(X[scaled_columns])

    return X.astype(float)


def explain_prediction(X, artifacts, top_n=5):
    """Reads the trained Logistic Regression model's own coefficients to
    rank each feature's contribution to THIS prediction (coefficient x
    the patient's own scaled/encoded value). Because Logistic Regression
    is linear in log-odds, this is an exact decomposition of the model's
    output for this patient — a genuine reading of the fitted model,
    consistent with the log-odds framing used for SHAP in Section 9.2 of
    the report, not a separately hand-written scoring rule."""

    model = artifacts["model"]
    columns = list(model.feature_names_in_)

    contributions = model.coef_[0] * X.iloc[0].values
    contrib_series = pd.Series(contributions, index=columns)
    contrib_series = contrib_series.reindex(
        contrib_series.abs().sort_values(ascending=False).index
    )

    drivers = []
    for feature, value in contrib_series.head(top_n).items():
        label = _friendly_name(feature)
        direction = "higher" if value > 0 else "lower"
        explanation = (
            f"{label} pushed this patient's predicted readmission log-odds "
            f"toward a {direction} probability (model coefficient x patient value)."
        )
        drivers.append((label, float(value), explanation))

    return drivers


# ==========================================================
# RISK ENGINE — runs the actual trained Logistic Regression pipeline
# (Task 05 / Model_Development.ipynb) instead of a hand-written rule set
# ==========================================================

def predict_readmission_risk(engineered_df):

    artifacts = load_artifacts()

    X = build_model_vector(engineered_df, artifacts)

    probability = float(artifacts["model"].predict_proba(X)[0, 1])

    probability_percent = int(np.clip(round(probability * 100), 1, 99))

    if probability_percent >= 65:
        risk_level = "High Risk"

    elif probability_percent >= 35:
        risk_level = "Moderate Risk"

    else:
        risk_level = "Low Risk"

    drivers = explain_prediction(X, artifacts)

    return probability_percent, risk_level, drivers


# ==========================================================
# CHART HELPERS
# ==========================================================

def render_gauge(probability_percent, risk_level):

    color = RISK_COLORS[risk_level]

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=probability_percent,

            number={
                "suffix": "%",
                "font": {
                    "size": 46,
                    "family": "Poppins",
                    "color": color
                }
            },

            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": MUTED,
                    "tickfont": {"color": MUTED, "size": 10}
                },
                "bar": {"color": color, "thickness": 0.28},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 35], "color": "rgba(31,170,107,0.10)"},
                    {"range": [35, 65], "color": "rgba(229,161,0,0.10)"},
                    {"range": [65, 100], "color": "rgba(226,61,91,0.10)"}
                ],
                "threshold": {
                    "line": {"color": color, "width": 3},
                    "thickness": 0.9,
                    "value": probability_percent
                }
            }
        )
    )

    fig.update_layout(
        height=270,
        margin=dict(t=5, b=5, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT}
    )

    return fig


def render_driver_chart(driver_df):

    colors = [
        HIGH if value >= 0 else LOW
        for value in driver_df["Impact"]
    ]

    fig = go.Figure(
        go.Bar(
            x=driver_df["Impact"],
            y=driver_df["Feature"],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0))
        )
    )

    fig.update_layout(
        height=max(220, 46 * len(driver_df)),
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT, "family": "Poppins"},
        xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, title="Impact"),
        yaxis=dict(autorange="reversed")
    )

    return fig


def render_summary_bar(risk_df):

    fig = px.bar(
        risk_df,
        x="Risk Level",
        y="Patients",
        color="Risk Level",
        color_discrete_map=RISK_COLORS,
        text="Patients"
    )

    fig.update_traces(textposition="outside", marker_line_width=0)

    fig.update_layout(
        height=320,
        showlegend=False,
        margin=dict(t=20, b=10, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": TEXT, "family": "Poppins"},
        xaxis=dict(gridcolor=BORDER),
        yaxis=dict(gridcolor=BORDER)
    )

    return fig


def risk_badge_html(risk_level):

    color = RISK_COLORS[risk_level]

    icon = {
        "Low Risk": "🟢",
        "Moderate Risk": "🟡",
        "High Risk": "🔴"
    }[risk_level]

    return f"""
    <span class="risk-badge"
          style="color:{color}; background:{color}18; border:1px solid {color}35;">
        {icon} {risk_level}
    </span>
    """


# ==========================================================
# UI HELPER FUNCTIONS
# ==========================================================

def render_navbar():
    """Top navigation bar with brand mark and live model status."""

    st.markdown(
        """
        <div class="navbar anim">
            <div class="navbar-brand">
                <div class="navbar-logo">🩺</div>
                <div>
                    <div class="navbar-title">SmartCare AI</div>
                    <div class="navbar-subtitle">CLINICAL INTELLIGENCE</div>
                </div>
            </div>
            <div class="navbar-status">
                <span class="pulse-dot"></span> AI Model Online
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_hero():
    """Hero section introducing the product."""

    st.markdown(
        """
        <div class="hero anim">
            <div class="hero-badge">🏥 SmartCare AI · Clinical Intelligence</div>
            <div class="hero-title">
                Predict <span>30-Day Readmission Risk</span> Before It Happens.
            </div>
            <div class="hero-description">
                An intelligent healthcare analytics platform that evaluates patient
                admission, clinical, utilization and billing information to estimate
                readmission risk and identify the key factors driving that prediction.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_metric_card(icon, value, label, accent):
    """Renders a single dashboard summary metric card."""

    st.markdown(
        f"""
        <div class="metric-card anim">
            <div class="metric-icon" style="background:{accent}18; color:{accent};">
                {icon}
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_dashboard_summary():
    """Row of live metric cards derived from this session's real activity
    (no fabricated clinical statistics)."""

    stats = st.session_state.setdefault(
        "session_stats",
        {"assessed": 0, "high_risk": 0, "probability_sum": 0}
    )

    assessed = stats["assessed"]
    high_risk = stats["high_risk"]
    avg_risk = (
        stats["probability_sum"] / assessed if assessed else 0
    )

    st.markdown('<div class="section-eyebrow">Session Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Live activity from this SmartCare AI session.</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric_card("🧑‍⚕️", f"{assessed:,}", "Patients Assessed", PRIMARY)
    with c2:
        render_metric_card("⚠️", f"{high_risk:,}", "High Risk Patients", HIGH)
    with c3:
        render_metric_card("📈", f"{avg_risk:.1f}%", "Average Risk (Session)", MODERATE)
    with c4:
        render_metric_card("🧠", "Logistic Regression", "Trained Model", PRIMARY)

    if st.button("🔮  Go to Risk Assessment →", use_container_width=True, key="dash_to_assessment"):
        st.session_state.page = "🔮 Risk Assessment"
        st.rerun()


def render_prediction_result(probability, risk_level, drivers, patient_id, erow):
    """Renders the full result panel: gauge, risk scale, interpretation."""

    color = RISK_COLORS[risk_level]

    st.plotly_chart(
        render_gauge(probability, risk_level),
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.markdown(risk_badge_html(risk_level), unsafe_allow_html=True)

    # Horizontal risk scale with position marker
    marker_pct = min(max(probability, 2), 98)

    st.markdown(
        f"""
        <div class="risk-scale">
            <div class="risk-scale-marker" style="left:{marker_pct}%;"></div>
        </div>
        <div class="risk-scale-labels">
            <span>Low</span><span>Moderate</span><span>High</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    interpretation = {
        "Low Risk": "This patient shows a low estimated probability of readmission "
                    "within 30 days based on the information provided.",
        "Moderate Risk": "This patient shows a moderate estimated probability of "
                          "readmission within 30 days and may benefit from routine follow-up.",
        "High Risk": "This patient has an elevated estimated probability of "
                      "readmission within 30 days and may warrant closer clinical review."
    }[risk_level]

    st.markdown(
        f"""
        <div class="result-interpretation" style="margin-top:14px; padding:14px 16px;
             background:{color}0D; border:1px solid {color}30; border-radius:12px;">
            <div style="font-weight:700; color:{TEXT}; font-size:0.85rem; margin-bottom:4px;">
                Risk Interpretation
            </div>
            <div style="font-size:0.8rem; color:{TEXT_2}; line-height:1.55;">
                {interpretation}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    c1, c2 = st.columns(2)
    c1.metric("30-Day Readmission", "Yes" if probability >= 50 else "No")
    c2.metric("Patient ID", patient_id)

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="card-header" style="font-size:0.9rem;">'
        f'<span class="dot" style="color:{PRIMARY};"></span>'
        'Derived Patient Insights'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="chip-row">
            <div class="chip">Total Bill <b>LKR {erow['total_bill_lkr']:,.0f}</b></div>
            <div class="chip">BMI <b>{erow['bmi_category']}</b></div>
            <div class="chip">BP <b>{erow['bp_category']}</b></div>
            <div class="chip">Prior Visits <b>{int(erow['total_prior_visits'])}</b></div>
            <div class="chip">Missed Rate <b>{erow['missed_appointment_rate']:.0%}</b></div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_risk_factors(driver_df):
    """Renders the 'Why is this patient at risk?' explainability section."""

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="card-header" style="font-size:0.9rem;">'
        f'<span class="dot" style="color:{PRIMARY};"></span>'
        'Why is this patient at risk?'
        '</div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        render_driver_chart(driver_df),
        use_container_width=True,
        config={"displayModeBar": False}
    )

    st.dataframe(
        driver_df[["Feature", "Explanation"]],
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "ℹ️ These factors are ranked by the trained Logistic Regression model's "
        "own coefficients for this patient (not SHAP, which is used in the "
        "Explainable AI notebook) and should support clinical review, not "
        "replace professional judgment."
    )


def render_clinical_insights(probability, risk_level, erow):
    """3-4 insight cards generated only from real available data."""

    st.markdown('<div class="section-eyebrow">Explainability</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Clinical Insights</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Summaries generated from the current patient\'s '
        'actual input and prediction data.</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">📊 Readmission Risk</div>
                <div class="insight-text">Current predicted probability is
                <b>{probability}%</b>, classified as <b>{risk_level}</b>.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">🏥 Utilization Pattern</div>
                <div class="insight-text">Total prior visits: <b>{int(erow['total_prior_visits'])}</b>.
                Missed appointment rate: <b>{erow['missed_appointment_rate']:.0%}</b>.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">🧬 Clinical Complexity</div>
                <div class="insight-text">BMI category: <b>{erow['bmi_category']}</b>.
                Blood pressure category: <b>{erow['bp_category']}</b>.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        review_flag = "Recommended" if risk_level != "Low Risk" else "Routine follow-up"
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">🔎 Recommended Review</div>
                <div class="insight-text"><b>{review_flag}</b> based on the current
                risk classification and derived utilization signals.</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_model_info():
    """Model information / transparency section."""

    st.markdown('<div class="section-eyebrow">Transparency</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">AI Model</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Details of the trained model powering '
        'SmartCare AI predictions.</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="card">', unsafe_allow_html=True)

    try:
        artifacts = load_artifacts()
        model_status = f"🟢 Loaded from {artifacts['base_dir']}/"
    except FileNotFoundError:
        model_status = "🔴 Model artifacts not found — see error above"

    rows = [
        ("Model Name", "Logistic Regression (Model_Development.ipynb, Task 05)"),
        ("Prediction Type", "30-Day Readmission Risk (probability)"),
        ("Number of Input Features", f"{len(REQUIRED_COLUMNS)}"),
        ("Preprocessing", "Same pipeline as Task 03 — feature engineering, "
                           "ordinal/one-hot encoding, StandardScaler scaling"),
        ("Decision Threshold", f"{DECISION_THRESHOLD:.2f} (matches notebook's "
                                "default .predict() cutoff)"),
        ("Explainability", "Ranked by the trained model's own coefficients"),
        ("Model Status", model_status),
    ]

    for label, value in rows:
        st.markdown(
            f"""
            <div class="info-row">
                <div class="info-label">{label}</div>
                <div class="info-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# SIDEBAR — real, working navigation
# ==========================================================
# Previously this was just a block of markdown text with emoji next to it —
# it looked like navigation but no click did anything. It's now a set of
# actual st.button() calls that write to st.session_state.page and rerun
# the app, and the whole page below reacts to st.session_state.page.

NAV_PAGES = ["🏠 Dashboard", "🔮 Risk Assessment", "🔍 Patient Insights", "⚙️ Model Information"]


def render_sidebar():
    """Sidebar with brand mark, live status, and clickable navigation."""

    if "page" not in st.session_state:
        st.session_state.page = "🏠 Dashboard"

    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding:6px 4px 18px 4px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <div style="width:36px; height:36px; border-radius:10px;
                         background:{PRIMARY}; display:flex; align-items:center;
                         justify-content:center; font-size:1rem;">🩺</div>
                    <div>
                        <div style="font-family:'Poppins',sans-serif; font-weight:700;
                             font-size:1.02rem; color:{SIDEBAR_TEXT};">SmartCare AI</div>
                        <div style="font-size:0.68rem; color:{SIDEBAR_MUTED}; font-weight:600;
                             letter-spacing:0.05em;">CLINICAL INTELLIGENCE</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div style="font-size:0.7rem; color:{SIDEBAR_MUTED}; font-weight:700; '
            'text-transform:uppercase; letter-spacing:0.06em; margin:4px 0 8px 2px;">'
            'Navigation</div>',
            unsafe_allow_html=True
        )

        for page_name in NAV_PAGES:
            is_active = st.session_state.page == page_name
            # This key drives the CSS selector .st-key-nav_active above,
            # which highlights whichever button is the current page.
            btn_key = "nav_active" if is_active else f"nav_{page_name}"
            if st.button(page_name, key=btn_key, use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

        st.markdown("---")

        st.markdown(
            f"""
            <div style="font-size:0.72rem; color:{SIDEBAR_MUTED}; font-weight:700;
                 text-transform:uppercase; letter-spacing:0.05em; margin-bottom:6px;">
                AI Model Status
            </div>
            <div class="navbar-status" style="display:inline-flex;">
                <span class="pulse-dot"></span> Online
            </div>
            """,
            unsafe_allow_html=True
        )


def render_footer():
    st.markdown(
        """
        <div class="footer">
            <strong>SmartCare AI</strong>
            · AI-Assisted Healthcare Analytics
            · 30-Day Readmission Risk Prediction
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# PAGE SECTIONS
# ==========================================================

def render_dashboard_page():
    render_hero()
    render_dashboard_summary()


def render_risk_assessment_page():

    st.markdown('<div class="section-eyebrow">Workspace</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Patient Risk Assessment</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">Enter patient information to estimate the probability '
        'of hospital readmission within 30 days.</div>',
        unsafe_allow_html=True
    )

    # ----------------------------------------------------------
    # Mode toggle — two standalone buttons (Single Patient / Batch CSV)
    # ----------------------------------------------------------

    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "single"

    nav_col1, nav_col2 = st.columns(2)

    with nav_col1:
        if st.button(
            "🔮  Single Patient Predictor",
            use_container_width=True,
            type="primary" if st.session_state.app_mode == "single" else "secondary"
        ):
            st.session_state.app_mode = "single"
            st.rerun()

    with nav_col2:
        if st.button(
            "📁  Batch CSV Analysis",
            use_container_width=True,
            type="primary" if st.session_state.app_mode == "batch" else "secondary"
        ):
            st.session_state.app_mode = "batch"
            st.rerun()

    app_mode = st.session_state.app_mode

    st.write("")

    # ========================================================
    # SINGLE PATIENT
    # ========================================================

    if app_mode == "single":

        # ------------------------------------------------------
        # SCENARIO REFERENCE CARDS (display only)
        # ------------------------------------------------------

        st.markdown(
            '<div class="card-header">'
            f'<span class="dot" style="color:{PRIMARY};"></span>'
            '⚡ Quick Clinical Scenarios'
            '</div>',
            unsafe_allow_html=True
        )

        presets = {

            "🚨 High Risk ICU": {
                "accent": HIGH,
                "desc": "ICU admission with prolonged stay and high treatment cost.",
                "values": dict(
                    age=68, gender="Male", room_type="ICU", admitted=1,
                    length_of_stay_days=7, previous_admissions=3,
                    systolic_bp=150, diastolic_bp=95, room_charge_lkr=45000,
                    appointment_status="Completed", diagnosis="Chest Pain",
                    department="Cardiology"
                )
            },

            "✅ Low Risk Outpatient": {
                "accent": LOW,
                "desc": "Routine outpatient visit with normal vitals and no admission.",
                "values": dict(
                    age=34, gender="Female", room_type="Not Admitted", admitted=0,
                    length_of_stay_days=0, previous_admissions=0,
                    systolic_bp=115, diastolic_bp=75, room_charge_lkr=0,
                    appointment_status="Completed", diagnosis="Migraine",
                    department="General Medicine"
                )
            },

            "⚠️ Moderate Inpatient": {
                "accent": MODERATE,
                "desc": "Three-day ward stay with elevated blood pressure.",
                "values": dict(
                    age=52, gender="Male", room_type="General Ward", admitted=1,
                    length_of_stay_days=3, previous_admissions=1,
                    systolic_bp=135, diastolic_bp=88, room_charge_lkr=12000,
                    appointment_status="Completed", diagnosis="Pneumonia",
                    department="General Medicine"
                )
            },

            "🔎 Billing Anomaly": {
                "accent": PRIMARY,
                "desc": "Hospital stay recorded while room charge is zero.",
                "values": dict(
                    age=45, gender="Female", room_type="General Ward", admitted=1,
                    length_of_stay_days=4, previous_admissions=0,
                    systolic_bp=128, diastolic_bp=84, room_charge_lkr=0,
                    appointment_status="Completed", diagnosis="Fracture",
                    department="Orthopedics"
                )
            }
        }

        if "preset_values" not in st.session_state:
            st.session_state.preset_values = {}

        cols = st.columns(4)

        for i, (name, cfg) in enumerate(presets.items()):

            with cols[i]:

                st.markdown(
                    f"""
                    <div class="preset-card" style="--accent:{cfg['accent']}">
                        <div class="preset-title">{name}</div>
                        <div class="preset-desc">{cfg['desc']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button("Use this scenario", key=f"preset_{name}", use_container_width=True):
                    st.session_state.preset_values = cfg["values"]
                    st.rerun()

        st.write("")

        pv = st.session_state.preset_values

        # ------------------------------------------------------
        # MAIN COLUMNS
        # ------------------------------------------------------

        left, right = st.columns([1.45, 1], gap="large")

        # ======================================================
        # LEFT FORM
        # ======================================================

        with left:

            # ---------------- Demographics ----------------

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(
                '<div class="card-header">'
                f'<span class="dot" style="color:{PRIMARY};"></span>'
                '🧑‍⚕️ Patient Demographics'
                '</div>',
                unsafe_allow_html=True
            )

            patient_id = st.text_input("Patient ID", "P10088")

            c1, c2, c3 = st.columns(3)

            with c1:
                age = st.number_input("Age", 1, 100, pv.get("age", 50))

                gender = st.selectbox(
                    "Gender", ["Male", "Female"],
                    index=["Male", "Female"].index(pv.get("gender", "Male"))
                )

            with c2:
                blood_group = st.selectbox(
                    "Blood Group",
                    ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
                )

                departments = [
                    "General Medicine", "Cardiology", "Neurology", "Orthopedics",
                    "Pediatrics", "Radiology", "Laboratory Services"
                ]

                department = st.selectbox(
                    "Department", departments,
                    index=departments.index(pv.get("department", "General Medicine"))
                )

            with c3:
                diagnoses = [
                    "Migraine", "Diabetes", "Back Pain", "Asthma", "Hypertension",
                    "Fracture", "Kidney Infection", "Pneumonia", "Fever", "Chest Pain"
                ]

                diagnosis = st.selectbox(
                    "Diagnosis", diagnoses,
                    index=diagnoses.index(pv.get("diagnosis", "Migraine"))
                )

                statuses = ["Completed", "No-Show", "Cancelled", "Scheduled"]

                appointment_status = st.selectbox(
                    "Appointment Status", statuses,
                    index=statuses.index(pv.get("appointment_status", "Completed"))
                )

            st.markdown('</div>', unsafe_allow_html=True)

            # ---------------- Hospital Utilization ----------------

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(
                '<div class="card-header">'
                f'<span class="dot" style="color:{PRIMARY};"></span>'
                '🛏️ Hospital Utilization & History'
                '</div>',
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                admitted = st.selectbox(
                    "Admission Status", [1, 0],
                    index=[1, 0].index(pv.get("admitted", 0)),
                    format_func=lambda x: "Inpatient" if x == 1 else "Outpatient"
                )

                room_types = ["Not Admitted", "General Ward", "Private Room", "ICU", "Unknown"]

                room_type = st.selectbox(
                    "Room Type", room_types,
                    index=room_types.index(pv.get("room_type", "Not Admitted"))
                )

            with c2:
                length_of_stay_days = st.number_input(
                    "Length of Stay (Days)", 0, 30, pv.get("length_of_stay_days", 2)
                )

                previous_admissions = st.number_input(
                    "Previous Admissions", 0, 10, pv.get("previous_admissions", 0)
                )

            with c3:
                previous_appointments = st.number_input("Previous Appointments", 0, 20, 2)
                missed_previous_appointments = st.number_input("Missed Appointments", 0, 10, 0)

            c4, c5, c6 = st.columns(3)

            with c4:
                waiting_days = st.number_input("Waiting Days", 0, 60, 2)

            with c5:
                appointment_date = st.date_input(
                    "Appointment Date", datetime.date(2025, 8, 8)
                )

            with c6:
                payment_statuses = ["Paid", "Unpaid", "Partially Paid"]
                payment_status = st.selectbox("Payment Status", payment_statuses)

            payment_methods = ["Insurance", "Online", "Cash", "Card"]
            payment_method = st.selectbox("Payment Method", payment_methods)

            st.caption(
                "Payment status and method options are verified against "
                "smartcare_ai_dataset_1000.csv."
            )

            st.markdown('</div>', unsafe_allow_html=True)

            # ---------------- Clinical Information ----------------

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(
                '<div class="card-header">'
                f'<span class="dot" style="color:{PRIMARY};"></span>'
                '💓 Clinical & Laboratory Information'
                '</div>',
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                systolic_bp = st.number_input("Systolic BP", 70, 220, pv.get("systolic_bp", 120))
                diastolic_bp = st.number_input("Diastolic BP", 40, 130, pv.get("diastolic_bp", 80))

            with c2:
                blood_sugar_mg_dl = st.number_input("Blood Sugar (mg/dL)", 50, 350, 100)
                cholesterol_mg_dl = st.number_input("Cholesterol (mg/dL)", 100, 400, 180)

            with c3:
                bmi = st.number_input("BMI", 10.0, 50.0, 23.0)
                lab_tests_count = st.number_input("Lab Tests", 0, 15, 1)

            treatments_count = st.number_input("Treatments / Procedures", 0, 15, 1)

            st.markdown('</div>', unsafe_allow_html=True)

            # ---------------- Billing & Utilization ----------------

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(
                '<div class="card-header">'
                f'<span class="dot" style="color:{PRIMARY};"></span>'
                '💰 Billing & Healthcare Utilization'
                '</div>',
                unsafe_allow_html=True
            )

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                consultation_fee_lkr = st.number_input("Consultation", 0, 50000, 3000)
            with c2:
                room_charge_lkr = st.number_input("Room Charge", 0, 200000, pv.get("room_charge_lkr", 0))
            with c3:
                lab_charge_lkr = st.number_input("Lab Charge", 0, 100000, 5000)
            with c4:
                medicine_charge_lkr = st.number_input("Medicine", 0, 150000, 10000)

            st.markdown('</div>', unsafe_allow_html=True)

            # ---------------- Predict button ----------------

            run = st.button(
                "Predict Readmission Risk →", use_container_width=True, key="predict_btn"
            )

        # ======================================================
        # RIGHT RESULT PANEL
        # ======================================================

        with right:

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.markdown(
                '<div class="card-header">'
                f'<span class="dot" style="color:{PRIMARY};"></span>'
                '🎯 AI Risk Assessment'
                '</div>',
                unsafe_allow_html=True
            )

            if run:

                with st.spinner("Running SmartCare AI risk model..."):

                    patient_dict = dict(
                        patient_id=patient_id, age=age, gender=gender,
                        blood_group=blood_group, department=department,
                        diagnosis=diagnosis, appointment_status=appointment_status,
                        admitted=admitted, room_type=room_type,
                        length_of_stay_days=length_of_stay_days,
                        previous_admissions=previous_admissions,
                        systolic_bp=systolic_bp, diastolic_bp=diastolic_bp,
                        blood_sugar_mg_dl=blood_sugar_mg_dl,
                        cholesterol_mg_dl=cholesterol_mg_dl, bmi=bmi,
                        lab_tests_count=lab_tests_count,
                        treatments_count=treatments_count,
                        consultation_fee_lkr=consultation_fee_lkr,
                        room_charge_lkr=room_charge_lkr,
                        lab_charge_lkr=lab_charge_lkr,
                        medicine_charge_lkr=medicine_charge_lkr,
                        waiting_days=waiting_days,
                        previous_appointments=previous_appointments,
                        missed_previous_appointments=missed_previous_appointments,
                        appointment_date=appointment_date,
                        payment_status=payment_status,
                        payment_method=payment_method
                    )

                    engineered_df = preprocess_and_engineer_features(patient_dict)
                    probability, risk_level, drivers = predict_readmission_risk(engineered_df)
                    erow = engineered_df.iloc[0]

                # Track real session stats (no fabricated data)
                stats = st.session_state.setdefault(
                    "session_stats", {"assessed": 0, "high_risk": 0, "probability_sum": 0}
                )
                stats["assessed"] += 1
                stats["probability_sum"] += probability
                if risk_level == "High Risk":
                    stats["high_risk"] += 1

                render_prediction_result(probability, risk_level, drivers, patient_id, erow)

                driver_df = pd.DataFrame(drivers, columns=["Feature", "Impact", "Explanation"])
                render_risk_factors(driver_df)

                # store for Patient Insights section
                st.session_state["last_prediction"] = {
                    "probability": probability,
                    "risk_level": risk_level,
                    "erow": erow,
                    "patient_id": patient_id
                }

            else:

                st.markdown(
                    f"""
                    <div style="text-align:center; padding:55px 20px;">
                        <div style="font-size:3.5rem; margin-bottom:15px;">🩺</div>
                        <div style="font-family:'Poppins'; font-size:1.2rem; font-weight:700;
                             color:{TEXT}; margin-bottom:8px;">
                            Ready for assessment
                        </div>
                        <div style="color:{MUTED}; font-size:0.85rem; line-height:1.6;
                             max-width:340px; margin:auto;">
                            Enter patient information on the left, then calculate the
                            estimated 30-day readmission risk.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown('</div>', unsafe_allow_html=True)

    # ========================================================
    # BATCH PROCESSING
    # ========================================================

    else:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        uploaded_file = st.file_uploader("📁 Upload SmartCare Patient CSV", type=["csv"])

        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded_file is None:

            st.markdown(
                f"""
                <div class="card">
                    <div style="text-align:center; padding:45px 20px;">
                        <div style="font-size:3rem; margin-bottom:12px;">📊</div>
                        <div style="font-family:'Poppins'; font-size:1.2rem; font-weight:700;
                             color:{TEXT};">
                            Upload your patient dataset
                        </div>
                        <div style="color:{MUTED}; margin-top:8px; font-size:0.82rem;">
                            CSV files containing the required SmartCare patient fields
                            are supported.
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            batch_df = pd.read_csv(uploaded_file)

            st.success(f"Successfully loaded {len(batch_df):,} patient records.")

            if batch_df.empty:

                st.error("The uploaded CSV does not contain any records.")

            else:

                missing_columns = [c for c in REQUIRED_COLUMNS if c not in batch_df.columns]

                if missing_columns:

                    st.error("The uploaded CSV is missing required columns.")
                    st.write(missing_columns)

                else:

                    st.success("✅ Dataset structure validated successfully.")

                    st.markdown('<div class="card">', unsafe_allow_html=True)

                    st.markdown(
                        '<div class="card-header">'
                        f'<span class="dot" style="color:{PRIMARY};"></span>'
                        '📋 Patient Dataset'
                        '</div>',
                        unsafe_allow_html=True
                    )

                    st.dataframe(batch_df, use_container_width=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                    run_batch = st.button(
                        "Run Batch Prediction →", use_container_width=True, key="run_batch_btn"
                    )

                    if run_batch:

                        results = []
                        explanations = {}

                        total_patients = len(batch_df)

                        progress_bar = st.progress(0)
                        status_text = st.empty()

                        for index, row in batch_df.iterrows():

                            patient_id_value = row["patient_id"]

                            try:

                                patient_dict = {
                                    "patient_id": row["patient_id"],
                                    "age": float(row["age"]),
                                    "gender": row["gender"],
                                    "blood_group": row["blood_group"],
                                    "department": row["department"],
                                    "diagnosis": row["diagnosis"],
                                    "appointment_status": row["appointment_status"],
                                    "admitted": int(row["admitted"]),
                                    "room_type": row["room_type"],
                                    "length_of_stay_days": float(row["length_of_stay_days"]),
                                    "previous_admissions": float(row["previous_admissions"]),
                                    "systolic_bp": float(row["systolic_bp"]),
                                    "diastolic_bp": float(row["diastolic_bp"]),
                                    "blood_sugar_mg_dl": float(row["blood_sugar_mg_dl"]),
                                    "cholesterol_mg_dl": float(row["cholesterol_mg_dl"]),
                                    "bmi": float(row["bmi"]),
                                    "lab_tests_count": float(row["lab_tests_count"]),
                                    "treatments_count": float(row["treatments_count"]),
                                    "consultation_fee_lkr": float(row["consultation_fee_lkr"]),
                                    "room_charge_lkr": float(row["room_charge_lkr"]),
                                    "lab_charge_lkr": float(row["lab_charge_lkr"]),
                                    "medicine_charge_lkr": float(row["medicine_charge_lkr"]),
                                    "waiting_days": float(row["waiting_days"]),
                                    "previous_appointments": float(row["previous_appointments"]),
                                    "missed_previous_appointments":
                                        float(row["missed_previous_appointments"]),
                                    "appointment_date": row["appointment_date"],
                                    "payment_status": row["payment_status"],
                                    "payment_method": row["payment_method"]
                                }

                                engineered_df = preprocess_and_engineer_features(patient_dict)

                                probability, risk_level, drivers = predict_readmission_risk(
                                    engineered_df
                                )

                                prediction = "Yes" if probability >= 50 else "No"

                                results.append({
                                    "patient_id": patient_id_value,
                                    "readmitted_within_30_days": prediction,
                                    "readmission_probability": probability,
                                    "risk_level": risk_level
                                })

                                explanations[str(patient_id_value)] = drivers

                            except Exception as error:

                                results.append({
                                    "patient_id": patient_id_value,
                                    "readmitted_within_30_days": "Error",
                                    "readmission_probability": None,
                                    "risk_level": str(error)
                                })

                            progress = (index + 1) / total_patients
                            progress_bar.progress(progress)
                            status_text.text(
                                f"Processing patient {index + 1:,} of {total_patients:,}"
                            )

                        progress_bar.empty()
                        status_text.success("✅ Batch prediction completed successfully.")

                        results_df = pd.DataFrame(results)

                        st.session_state["batch_results"] = results_df
                        st.session_state["batch_explanations"] = explanations

                        # Track real session stats
                        valid = results_df[results_df["readmitted_within_30_days"] != "Error"]
                        stats = st.session_state.setdefault(
                            "session_stats", {"assessed": 0, "high_risk": 0, "probability_sum": 0}
                        )
                        stats["assessed"] += len(valid)
                        stats["high_risk"] += int((valid["risk_level"] == "High Risk").sum())
                        stats["probability_sum"] += float(
                            valid["readmission_probability"].sum()
                        )

                    # --------------------------------------------------
                    # RESULTS
                    # --------------------------------------------------

                    if "batch_results" in st.session_state:

                        results_df = st.session_state["batch_results"]
                        explanations = st.session_state["batch_explanations"]

                        st.markdown('<div class="card">', unsafe_allow_html=True)

                        st.markdown(
                            '<div class="card-header">'
                            f'<span class="dot" style="color:{PRIMARY};"></span>'
                            '🎯 Prediction Results'
                            '</div>',
                            unsafe_allow_html=True
                        )

                        st.dataframe(results_df, use_container_width=True)

                        st.markdown('</div>', unsafe_allow_html=True)

                        valid_results = results_df[
                            results_df["readmitted_within_30_days"] != "Error"
                        ]

                        if not valid_results.empty:

                            predicted_yes = (
                                valid_results["readmitted_within_30_days"] == "Yes"
                            ).sum()
                            predicted_no = (
                                valid_results["readmitted_within_30_days"] == "No"
                            ).sum()
                            high_risk = (valid_results["risk_level"] == "High Risk").sum()
                            moderate_risk = (valid_results["risk_level"] == "Moderate Risk").sum()
                            low_risk = (valid_results["risk_level"] == "Low Risk").sum()

                            st.markdown('<div class="card">', unsafe_allow_html=True)

                            st.markdown(
                                '<div class="card-header">'
                                f'<span class="dot" style="color:{PRIMARY};"></span>'
                                '📊 Population Risk Overview'
                                '</div>',
                                unsafe_allow_html=True
                            )

                            col1, col2, col3, col4 = st.columns(4)

                            col1.metric("Patients", f"{len(valid_results):,}")
                            col2.metric("Predicted Readmission", f"{predicted_yes:,}")
                            col3.metric("No Readmission", f"{predicted_no:,}")
                            col4.metric("High Risk", f"{high_risk:,}")

                            risk_df = pd.DataFrame({
                                "Risk Level": ["High Risk", "Moderate Risk", "Low Risk"],
                                "Patients": [high_risk, moderate_risk, low_risk]
                            })

                            st.plotly_chart(
                                render_summary_bar(risk_df),
                                use_container_width=True,
                                config={"displayModeBar": False}
                            )

                            st.markdown('</div>', unsafe_allow_html=True)

                            # ------------------------------------------
                            # PATIENT-LEVEL EXPLANATION
                            # ------------------------------------------

                            st.markdown('<div class="card">', unsafe_allow_html=True)

                            st.markdown(
                                '<div class="card-header">'
                                f'<span class="dot" style="color:{PRIMARY};"></span>'
                                '🔍 Patient-Level Explanation'
                                '</div>',
                                unsafe_allow_html=True
                            )

                            patient_options = valid_results["patient_id"].astype(str).tolist()

                            selected_patient = st.selectbox("Select a patient", patient_options)

                            selected_row = valid_results[
                                valid_results["patient_id"].astype(str) == selected_patient
                            ]

                            if not selected_row.empty:

                                selected_probability = selected_row.iloc[0][
                                    "readmission_probability"
                                ]
                                selected_prediction = selected_row.iloc[0][
                                    "readmitted_within_30_days"
                                ]
                                selected_risk = selected_row.iloc[0]["risk_level"]

                                c1, c2, c3 = st.columns(3)
                                c1.metric("Prediction", selected_prediction)
                                c2.metric("Probability", f"{selected_probability}%")
                                c3.metric("Risk Level", selected_risk)

                                st.markdown(risk_badge_html(selected_risk), unsafe_allow_html=True)

                                selected_drivers = explanations.get(selected_patient, [])

                                if selected_drivers:

                                    explanation_df = pd.DataFrame(
                                        selected_drivers,
                                        columns=["Feature", "Impact", "Explanation"]
                                    )

                                    st.write("")

                                    st.plotly_chart(
                                        render_driver_chart(explanation_df),
                                        use_container_width=True,
                                        config={"displayModeBar": False}
                                    )

                                    st.dataframe(
                                        explanation_df, use_container_width=True, hide_index=True
                                    )

                            st.markdown('</div>', unsafe_allow_html=True)

                            # ------------------------------------------
                            # GLOBAL DRIVERS
                            # ------------------------------------------

                            st.markdown('<div class="card">', unsafe_allow_html=True)

                            st.markdown(
                                '<div class="card-header">'
                                f'<span class="dot" style="color:{PRIMARY};"></span>'
                                '📈 Overall Risk Drivers'
                                '</div>',
                                unsafe_allow_html=True
                            )

                            all_driver_rows = []

                            for patient_id_key, driver_list in explanations.items():
                                for driver in driver_list:
                                    all_driver_rows.append({
                                        "Patient": patient_id_key,
                                        "Feature": driver[0],
                                        "Impact": abs(driver[1])
                                    })

                            if all_driver_rows:

                                all_driver_df = pd.DataFrame(all_driver_rows)

                                global_driver_df = (
                                    all_driver_df.groupby("Feature", as_index=False)["Impact"]
                                    .mean()
                                    .sort_values("Impact", ascending=False)
                                )

                                fig_global = px.bar(
                                    global_driver_df, x="Impact", y="Feature", orientation="h"
                                )

                                fig_global.update_traces(marker_color=PRIMARY, marker_line_width=0)

                                fig_global.update_layout(
                                    height=360,
                                    showlegend=False,
                                    margin=dict(t=10, b=10, l=10, r=10),
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    font={"color": TEXT},
                                    xaxis={"gridcolor": BORDER},
                                    yaxis={"gridcolor": BORDER, "autorange": "reversed"}
                                )

                                st.plotly_chart(
                                    fig_global,
                                    use_container_width=True,
                                    config={"displayModeBar": False}
                                )

                            st.markdown('</div>', unsafe_allow_html=True)

                        # ----------------------------------------------
                        # DOWNLOAD
                        # ----------------------------------------------

                        csv_data = results_df.to_csv(index=False).encode("utf-8")

                        st.download_button(
                            label="⬇️  Download Prediction Results",
                            data=csv_data,
                            file_name="smartcare_batch_predictions.csv",
                            mime="text/csv",
                            use_container_width=True
                        )


def render_patient_insights_page():

    if "last_prediction" in st.session_state:
        lp = st.session_state["last_prediction"]
        render_clinical_insights(lp["probability"], lp["risk_level"], lp["erow"])
    else:
        st.markdown('<div class="section-eyebrow">Explainability</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Clinical Insights</div>', unsafe_allow_html=True)
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="text-align:center; padding:45px 20px;">
                <div style="font-size:3rem; margin-bottom:12px;">🔍</div>
                <div style="font-family:'Poppins'; font-size:1.15rem; font-weight:700;
                     color:{TEXT};">
                    No prediction yet
                </div>
                <div style="color:{MUTED}; margin-top:8px; font-size:0.85rem;
                     max-width:360px; margin-left:auto; margin-right:auto;">
                    Run a single-patient risk assessment first — insights for that
                    patient will show up here automatically.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🔮  Go to Risk Assessment →", use_container_width=True, key="insights_to_assessment"):
            st.session_state.page = "🔮 Risk Assessment"
            st.rerun()


# ==========================================================
# APP SHELL
# ==========================================================

inject_custom_css()
render_sidebar()
render_navbar()

current_page = st.session_state.get("page", "🏠 Dashboard")

if current_page == "🏠 Dashboard":
    render_dashboard_page()
elif current_page == "🔮 Risk Assessment":
    render_risk_assessment_page()
elif current_page == "🔍 Patient Insights":
    render_patient_insights_page()
elif current_page == "⚙️ Model Information":
    render_model_info()

st.write("")
render_footer()