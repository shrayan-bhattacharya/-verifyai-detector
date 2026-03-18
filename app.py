"""
VerifyAI — AI Report Auditor
Streamlit UI: upload source documents, paste an AI-generated report,
receive a claim-by-claim hallucination audit with exact citations.
"""

import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VerifyAI — AI Report Auditor",
    page_icon="🛡️",
    layout="wide",
)

# ── Load API key ──────────────────────────────────────────────────────────────
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

def _get_api_key() -> str | None:
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("ANTHROPIC_API_KEY")

# ── Corporate CSS design system ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ══════════════════════════════════════════════════════
   DESIGN TOKENS
══════════════════════════════════════════════════════ */
:root {
    --navy:         #1B2A4A;
    --navy-mid:     #243557;
    --accent:       #2E6EA6;
    --accent-light: #3D84C8;
    --success:      #2D8B4E;
    --success-bg:   #EAF6EE;
    --success-bd:   #A3D9B1;
    --error:        #C0392B;
    --error-bg:     #FBEAEA;
    --warning:      #B8860B;
    --warning-bg:   #FEF9E7;
    --gray-50:      #F8F9FA;
    --gray-100:     #EAECEF;
    --gray-300:     #CED4DA;
    --gray-500:     #6C757D;
    --gray-700:     #495057;
    --gray-900:     #212529;
    --white:        #FFFFFF;
    --page-bg:      #F4F6F9;
}

/* ══════════════════════════════════════════════════════
   GLOBAL LIGHT THEME — force every Streamlit layer
══════════════════════════════════════════════════════ */
html, body {
    background-color: var(--page-bg) !important;
    color: var(--gray-900) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

/* Root app shell */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="block-container"],
div[class*="block-container"],
div[class*="appview-container"],
section[data-testid="stMain"] {
    background-color: var(--page-bg) !important;
    color: var(--gray-900) !important;
}

/* Sidebar — every layer */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div,
[data-testid="stSidebar"] > div > div,
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] {
    background-color: var(--white) !important;
    color: var(--gray-900) !important;
    border-right: 1px solid var(--gray-100) !important;
}

/* All markdown / paragraph text inside sidebar */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: var(--gray-900) !important;
    background-color: transparent !important;
}

/* All text globally */
p, span, label, h1, h2, h3, h4, h5, h6,
.stMarkdown p, .stMarkdown span,
[data-testid="stText"],
[data-testid="stCaptionContainer"] {
    color: var(--gray-900) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ══════════════════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════════════════ */
/* All secondary/default buttons — accent blue, white text */
.stButton > button,
.stButton > button:focus,
[data-testid="stBaseButton-secondary"] {
    background-color: var(--accent) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 1.25rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.15) !important;
    transition: background-color 0.15s ease !important;
}
.stButton > button:hover,
[data-testid="stBaseButton-secondary"]:hover {
    background-color: var(--accent-light) !important;
    color: var(--white) !important;
}
.stButton > button:disabled,
[data-testid="stBaseButton-secondary"]:disabled {
    background-color: var(--gray-300) !important;
    color: var(--gray-500) !important;
    cursor: not-allowed !important;
    box-shadow: none !important;
}

/* Primary button (Streamlit 1.55+ selector) — navy, white text, larger */
[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"] {
    background-color: var(--navy) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.625rem 1.75rem !important;
    box-shadow: 0 2px 4px rgba(27,42,74,0.25) !important;
}
[data-testid="stBaseButton-primary"]:hover,
.stButton > button[kind="primary"]:hover {
    background-color: var(--navy-mid) !important;
    color: var(--white) !important;
}
/* Force all p/span inside any button to inherit white */
.stButton button p,
.stButton button span {
    color: inherit !important;
}

.stDownloadButton > button {
    background-color: var(--white) !important;
    color: var(--accent) !important;
    border: 1.5px solid var(--accent) !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    background-color: #EAF2FA !important;
}

/* ══════════════════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════════════════ */
/* Track */
.stProgress > div > div {
    background-color: var(--gray-100) !important;
    border-radius: 4px !important;
}
/* Fill */
.stProgress > div > div > div {
    background-color: var(--accent) !important;
    border-radius: 4px !important;
}
/* Label text — remove any blue highlight */
.stProgress,
.stProgress p,
.stProgress span,
.stProgress > div > p,
[data-testid="stProgress"] p,
[data-testid="stProgress"] span {
    color: var(--navy) !important;
    background-color: transparent !important;
    background: transparent !important;
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
}

/* ══════════════════════════════════════════════════════
   TEXT AREA
══════════════════════════════════════════════════════ */
.stTextArea textarea {
    background-color: var(--white) !important;
    color: var(--gray-900) !important;
    border: 1.5px solid var(--gray-300) !important;
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    line-height: 1.65 !important;
}
.stTextArea textarea:focus {
    background-color: var(--white) !important;
    color: var(--gray-900) !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(46,110,166,0.12) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #ADB5BD !important; }
.stTextArea label {
    color: var(--gray-900) !important;
    font-weight: 500 !important;
}

/* ══════════════════════════════════════════════════════
   FILE UPLOADER
══════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background-color: var(--gray-50) !important;
    border: 1.5px dashed var(--gray-300) !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] * {
    background-color: transparent !important;
    color: var(--gray-700) !important;
}
[data-testid="stFileUploader"] button {
    background-color: var(--white) !important;
    color: var(--accent) !important;
    border: 1px solid var(--accent) !important;
}

/* ══════════════════════════════════════════════════════
   SPINNER
══════════════════════════════════════════════════════ */
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span {
    color: var(--navy) !important;
    background: transparent !important;
}

/* ══════════════════════════════════════════════════════
   COMPONENT CLASSES
══════════════════════════════════════════════════════ */

/* Feature cards */
.vai-feature-card {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-radius: 10px;
    padding: 1.5rem 1.25rem 1.25rem;
    text-align: center;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    box-sizing: border-box;
    width: 100%;
}
.vai-feature-icon  { font-size: 1.75rem; display: block; margin-bottom: 0.65rem; }
.vai-feature-title { font-weight: 600; color: var(--navy); font-size: 0.9375rem; margin-bottom: 0.4rem; display: block; }
.vai-feature-desc  { color: var(--gray-500); font-size: 0.8125rem; line-height: 1.55; display: block; }

/* Generic content card */
.vai-card {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-radius: 10px;
    padding: 1.25rem 1.125rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    box-sizing: border-box;
}

/* Section headers */
.vai-section-header {
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--gray-500) !important;
    margin: 0 0 0.875rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--gray-100);
    background: transparent !important;
}

/* Metric cards */
.vai-metric {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-radius: 10px;
    padding: 1.25rem 1rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.vai-metric-label {
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--gray-500) !important;
    margin-bottom: 0.3rem;
    display: block;
}
.vai-metric-value { font-size: 1.875rem; font-weight: 700; line-height: 1.1; display: block; }
.vai-metric-navy  { color: var(--navy) !important; }
.vai-metric-green { color: var(--success) !important; }
.vai-metric-red   { color: var(--error) !important; }
.vai-metric-amber { color: var(--warning) !important; }

/* Trust score block */
.vai-trust-block {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-radius: 10px;
    padding: 1.5rem 1.75rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.vai-trust-label {
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--gray-500) !important;
    display: block;
    margin-bottom: 0.2rem;
}
.vai-trust-score { font-size: 2.75rem; font-weight: 700; line-height: 1; display: block; margin-bottom: 0.2rem; }
.vai-trust-sub   { font-size: 0.8rem; color: var(--gray-500) !important; display: block; margin-top: 0.3rem; }

/* Issue cards */
.vai-issue-incorrect {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-left: 4px solid var(--error) !important;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    box-sizing: border-box;
}
.vai-issue-unverifiable {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-left: 4px solid var(--warning) !important;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    box-sizing: border-box;
}
.vai-issue-claim  { font-size: 0.9375rem; font-weight: 500; color: var(--gray-900) !important; margin-bottom: 0.4rem; display: block; }
.vai-issue-meta   { font-size: 0.8125rem; color: var(--gray-500) !important; line-height: 1.5; display: block; }
.vai-issue-source { font-size: 0.8125rem; color: var(--gray-700) !important; margin-top: 0.3rem; display: block; }
.vai-cite         { font-size: 0.75rem; color: var(--accent) !important; font-style: italic; }

/* Badges */
.vai-badge {
    display: inline-block;
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    white-space: nowrap;
}
.vai-badge-verified   { background: #D4EDDA !important; color: #1A5E32 !important; }
.vai-badge-flagged    { background: #FADBD8 !important; color: #7B2020 !important; }
.vai-badge-unverified { background: #FEF9E7 !important; color: #7D5A00 !important; border: 1px solid #F0D060; }
.vai-conf-tag         { font-size: 0.6875rem; color: var(--gray-500) !important; font-weight: 500; }
.vai-claim-text       { font-size: 0.875rem; font-weight: 500; color: var(--gray-900) !important; display: block; }
.vai-claim-sub        { font-size: 0.8rem; color: var(--gray-500) !important; margin-top: 0.2rem; line-height: 1.45; display: block; }

/* Logo */
.vai-logo-title {
    font-size: 1.375rem;
    font-weight: 700;
    color: var(--navy) !important;
    letter-spacing: -0.01em;
}
.vai-logo-sub {
    font-size: 0.75rem;
    color: var(--gray-500) !important;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-top: 0.1rem;
}
.vai-hr { border: none; border-top: 1px solid var(--gray-100); margin: 1rem 0; }

/* Status card (success) */
.vai-status-card {
    background: var(--success-bg) !important;
    border: 1px solid var(--success-bd);
    border-radius: 8px;
    padding: 0.875rem 1rem;
    font-size: 0.875rem;
    color: var(--success) !important;
    font-weight: 500;
    box-sizing: border-box;
}
.vai-status-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.2rem;
    font-size: 0.8125rem;
    color: var(--gray-700) !important;
    background: transparent !important;
}

/* Info banner */
.vai-info-banner {
    background: #EAF2FA !important;
    border: 1px solid #BDD7EF;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-size: 0.875rem;
    color: #1B4F72 !important;
    box-sizing: border-box;
    width: 100%;
}

/* Main header */
.vai-main-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--navy) !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}
.vai-main-sub {
    font-size: 1rem;
    color: var(--gray-500) !important;
    font-weight: 400;
    margin-bottom: 1.75rem;
}

/* Sidebar footer */
.vai-sidebar-footer {
    font-size: 0.75rem;
    color: var(--gray-500) !important;
    text-align: center;
    padding: 0.5rem 0;
    background: transparent !important;
}
.vai-sidebar-footer strong { color: var(--gray-700) !important; }
.vai-sidebar-footer a      { color: var(--accent) !important; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────────────────────
if "collection"           not in st.session_state: st.session_state.collection           = None
if "chunks_count"         not in st.session_state: st.session_state.chunks_count         = 0
if "files_processed"      not in st.session_state: st.session_state.files_processed      = []
if "audit_results"        not in st.session_state: st.session_state.audit_results        = None
if "audit_summary"        not in st.session_state: st.session_state.audit_summary        = None
if "report_text"          not in st.session_state: st.session_state.report_text          = None
if "csv_data"             not in st.session_state: st.session_state.csv_data             = None
if "chroma_dir"           not in st.session_state: st.session_state.chroma_dir           = tempfile.mkdtemp()
if "report_text_from_file"  not in st.session_state: st.session_state.report_text_from_file  = ""
if "report_fname_cached"    not in st.session_state: st.session_state.report_fname_cached    = ""

# ── Default test report ────────────────────────────────────────────────────────
DG_TEST_REPORT = (
    "Dollar General Corporation reported total revenue of $34.2 billion for fiscal year 2021, "
    "a 1.4% increase from the prior year. "
    "The company operated 18,130 stores across 48 states. "
    "Net income reached $2.8 billion for the fiscal year. "
    "Dollar General opened 1,050 new stores and remodeled 1,750 locations. "
    "The company employed approximately 163,000 workers. "
    "Same-store sales decreased 2.8% versus fiscal 2020. "
    "Gross profit margin was 31.6%. "
    "CEO Todd Vasos announced plans to expand into Canada by 2023."
)

# ── Helper: file-type label ────────────────────────────────────────────────────
EXT_LABEL = {
    "pdf":  "PDF",
    "docx": "DOCX",
    "xlsx": "XLSX",
    "xls":  "XLS",
    "txt":  "TXT",
}

def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else "?"


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding:0 0.25rem">
        <div class="vai-logo-title">🛡️ VerifyAI</div>
        <div class="vai-logo-sub">AI Report Auditor</div>
    </div>
    <div class="vai-hr"></div>
    """, unsafe_allow_html=True)

    # Section header
    st.markdown('<p class="vai-section-header">Source Documents</p>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Upload PDFs, Excel, Word, or TXT files",
        accept_multiple_files=True,
        type=["pdf", "docx", "xlsx", "xls", "txt"],
        label_visibility="collapsed",
    )

    # Show uploaded file list
    if uploaded_files:
        for f in uploaded_files:
            ext = _ext(f.name)
            label = EXT_LABEL.get(ext, ext.upper())
            st.markdown(
                f'<div class="vai-status-item">'
                f'<span style="font-size:0.7rem;background:#EAECEF;padding:0.1rem 0.35rem;'
                f'border-radius:3px;font-weight:600;color:#495057">{label}</span>'
                f'<span style="color:#212529">{f.name}</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<p style="font-size:0.8rem;color:#6C757D;margin:0.5rem 0 1rem 0">'
            'Upload files above, then click Process to index them.</p>',
            unsafe_allow_html=True,
        )

    process_btn = st.button(
        "Process Documents",
        use_container_width=True,
        disabled=not bool(uploaded_files),
    )

    if process_btn:
        api_key = _get_api_key()
        if not api_key:
            st.error("ANTHROPIC_API_KEY not found.")
        else:
            from parse_files import parse_file
            from chunk_and_embed import chunk_with_metadata, create_vector_store

            n_files   = len(uploaded_files)
            prog      = st.progress(0, text="Starting…")
            all_blocks = []

            for idx, uf in enumerate(uploaded_files):
                pct = int((idx / n_files) * 70)
                prog.progress(pct, text=f"Parsing {uf.name}…  ({idx + 1}/{n_files})")
                blocks = parse_file(uf)
                all_blocks.extend(blocks)

            if not all_blocks:
                prog.empty()
                st.error("No readable content found in the uploaded files.")
            else:
                prog.progress(75, text="Chunking text…")
                chunks = chunk_with_metadata(all_blocks)

                prog.progress(85, text=f"Embedding {len(chunks)} chunks into vector store…")
                collection, _ = create_vector_store(chunks)

                prog.progress(100, text="Done.")
                prog.empty()

                st.session_state.collection      = collection
                st.session_state.chunks_count    = len(chunks)
                st.session_state.files_processed = [f.name for f in uploaded_files]
                st.session_state.audit_results   = None
                st.rerun()

    # Status card after processing
    if st.session_state.collection is not None:
        n_files  = len(st.session_state.files_processed)
        n_chunks = st.session_state.chunks_count
        st.markdown(
            f'<div class="vai-status-card">'
            f'✓ Sources loaded<br>'
            f'<span style="font-weight:400;font-size:0.8rem;color:#155724">'
            f'{n_files} file{"s" if n_files != 1 else ""} &nbsp;·&nbsp; {n_chunks} chunks indexed'
            f'</span></div>',
            unsafe_allow_html=True,
        )

    # Sidebar footer
    st.markdown("<br>" * 4, unsafe_allow_html=True)
    st.markdown(
        '<div class="vai-sidebar-footer">'
        'Built by <strong>Shrayan Bhattacharya</strong><br>'
        '<a href="https://github.com/shrayan-bhattacharya" target="_blank">github.com/shrayan-bhattacharya</a>'
        '</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN AREA — Header (always visible)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<p class="vai-main-title">AI Report Auditor</p>'
    '<p class="vai-main-sub">Automated verification of AI-generated reports against source documents.</p>',
    unsafe_allow_html=True,
)

# ── Landing state: no sources processed ──────────────────────────────────────
if st.session_state.collection is None:
    c1, c2, c3 = st.columns(3)
    cards = [
        ("📂", "Upload Sources",    "Upload PDFs, Excel files, or Word documents as your ground-truth source material."),
        ("📋", "Paste Report",      "Paste any AI-generated report to have every factual claim extracted automatically."),
        ("🛡️", "Get Audit Report",  "Receive a detailed verification with exact citations for every claim in the report."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], cards):
        with col:
            st.markdown(
                f'<div class="vai-feature-card">'
                f'<div class="vai-feature-icon">{icon}</div>'
                f'<div class="vai-feature-title">{title}</div>'
                f'<div class="vai-feature-desc">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="vai-info-banner">ℹ️&nbsp;&nbsp;'
        'Start by uploading source documents in the sidebar to the left.'
        '</div>',
        unsafe_allow_html=True,
    )

# ── Active state: sources loaded ─────────────────────────────────────────────
else:
    api_key = _get_api_key()
    if not api_key:
        st.error("ANTHROPIC_API_KEY not found. Add it to your .env file or Streamlit secrets.")
        st.stop()

    # ── 1. Report context ─────────────────────────────────────────────────────
    st.markdown(
        '<p class="vai-section-header">Report Context '
        '<span style="font-weight:400;text-transform:none;letter-spacing:0;font-size:0.75rem;'
        'color:#ADB5BD">(optional)</span></p>',
        unsafe_allow_html=True,
    )
    report_context = st.text_input(
        "Report Context",
        placeholder="e.g. This report was generated by an AI agent analyzing Dollar General's FY2021 annual report...",
        help="Helps Claude understand what the report is about when extracting and verifying claims.",
        label_visibility="collapsed",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 2. Report input ───────────────────────────────────────────────────────
    st.markdown(
        '<p class="vai-section-header">AI-Generated Report</p>'
        '<p style="font-size:0.8375rem;color:#6C757D;margin:-0.5rem 0 0.75rem 0">'
        'Upload a file <strong>or</strong> paste the report text below — file takes priority if both are provided.'
        '</p>',
        unsafe_allow_html=True,
    )

    report_file = st.file_uploader(
        "Upload AI-generated report",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
        key="report_file_uploader",
    )

    # Parse the report file as soon as it is selected.
    # Read raw bytes directly (avoids stream-state issues with UploadedFile),
    # then dispatch to the type-specific parser.
    if report_file is not None:
        if report_file.name != st.session_state.report_fname_cached:
            from parse_files import parse_pdf, parse_docx, parse_txt
            _ocr_notice = st.empty()
            try:
                _raw = report_file.getvalue()
                _fname = report_file.name
                _ext = _fname.lower()
                if _ext.endswith(".pdf"):
                    # First pass: check if pdfplumber finds text without OCR
                    import pdfplumber, io as _io
                    _has_text = False
                    with pdfplumber.open(_io.BytesIO(_raw)) as _pdf:
                        for _pg in _pdf.pages:
                            if (_pg.extract_text() or "").strip():
                                _has_text = True
                                break
                    if not _has_text:
                        _ocr_notice.info(
                            "Scanned PDF detected — extracting text via OCR "
                            "(this may take 10–30 seconds)…"
                        )
                    _blocks = parse_pdf(_raw, _fname)
                elif _ext.endswith(".docx"):
                    _blocks = parse_docx(_raw, _fname)
                elif _ext.endswith(".txt"):
                    _blocks = parse_txt(_raw, _fname)
                else:
                    _blocks = []
                _ocr_notice.empty()
                _text = "\n\n".join(b["text"] for b in _blocks if b["text"].strip())
                st.session_state.report_text_from_file = _text
                st.session_state.report_fname_cached   = _fname
            except Exception as _exc:
                _ocr_notice.empty()
                st.session_state.report_text_from_file = ""
                st.session_state.report_fname_cached   = ""
                st.error(f"Could not parse report file: {_exc}")

    report_paste = st.text_area(
        "Or paste the report text directly",
        value="",
        height=220,
        placeholder="Paste the AI-generated report you want to verify here...",
        label_visibility="collapsed",
    )

    # Confirmation badge — show only when a file is actively selected AND parsed
    if report_file is not None:
        _cached = st.session_state.report_text_from_file
        _matches = (st.session_state.report_fname_cached == report_file.name)
        if _cached and _matches:
            st.markdown(
                f'<div class="vai-status-card" style="margin-top:0.5rem">'
                f'✓ File ready: <strong>{report_file.name}</strong> — will be used for the audit.'
                f'</div>',
                unsafe_allow_html=True,
            )
        elif not _cached and _matches:
            st.warning(
                f"**No readable text found in {report_file.name}** — even after OCR. "
                f"The file may be encrypted, corrupted, or contain only non-text graphics. "
                f"Please paste the report text in the text area below instead."
            )

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Run Audit", use_container_width=False)

    # ── Run audit pipeline ────────────────────────────────────────────────────
    if run_btn:
        from claim_extractor  import extract_claims
        from claim_verifier   import verify_claim
        from report_generator import generate_report_summary, format_report_text, generate_csv_report

        # Resolve report text — file takes priority over pasted text.
        # Use cached file text only when a file is currently selected AND its
        # name matches what we parsed (guards against stale cache from a prior
        # session or a previously uploaded file that was then removed).
        _file_text = ""
        if (
            report_file is not None
            and st.session_state.report_fname_cached == report_file.name
            and st.session_state.report_text_from_file
        ):
            _file_text = st.session_state.report_text_from_file
        elif st.session_state.report_text_from_file and report_file is None:
            # Streamlit occasionally delivers report_file=None for one frame on a
            # button-click rerun even though the user never removed the file.
            # Fall back to whatever we last successfully parsed.
            _file_text = st.session_state.report_text_from_file

        report_text = _file_text or report_paste.strip()

        if not report_text:
            st.warning("Please upload a report file or paste report text above before running the audit.")
            st.stop()

        try:
            status_box = st.empty()
            prog = st.progress(0)

            # Step 1 — extract claims
            status_box.info("Step 1 of 2 — Extracting claims from the report…")
            claims = extract_claims(report_text, api_key, context=report_context)
            n = len(claims)
            prog.progress(10)

            # Step 2 — verify each claim
            results = []
            for i, item in enumerate(claims):
                status_box.info(f"Step 2 of 2 — Verifying claim {i + 1} of {n}…")
                r = verify_claim(
                    item["claim_text"],
                    st.session_state.collection,
                    api_key,
                    context=report_context,
                )
                r["claim_number"] = item["claim_number"]
                results.append(r)
                prog.progress(int(10 + 88 * (i + 1) / n))

            prog.progress(100)
            status_box.success(f"Audit complete — {n} claims verified.")

            summary    = generate_report_summary(results)
            report_out = format_report_text(summary)
            csv_out    = generate_csv_report(results)

            st.session_state.audit_results = results
            st.session_state.audit_summary = summary
            st.session_state.report_text   = report_out
            st.session_state.csv_data      = csv_out
            st.rerun()

        except Exception as exc:
            st.exception(exc)

    # ── Results display ───────────────────────────────────────────────────────
    if st.session_state.audit_results:
        summary = st.session_state.audit_summary
        results = st.session_state.audit_results

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="vai-section-header">Audit Summary</p>', unsafe_allow_html=True)

        # ── Metric cards ──────────────────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        metrics = [
            (m1, "Claims Analyzed",  summary["total_claims"],        "vai-metric-navy"),
            (m2, "Verified",         summary["correct_count"],       "vai-metric-green"),
            (m3, "Flagged",          summary["incorrect_count"],     "vai-metric-red"),
            (m4, "Unverifiable",     summary["unverifiable_count"],  "vai-metric-amber"),
        ]
        for col, label, val, css_cls in metrics:
            with col:
                st.markdown(
                    f'<div class="vai-metric">'
                    f'<div class="vai-metric-label">{label}</div>'
                    f'<div class="vai-metric-value {css_cls}">{val}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Trust score ───────────────────────────────────────────────────────
        trust = summary["trust_score"]
        if trust >= 80:
            trust_color = "#2D8B4E"
            trust_bar   = "#2D8B4E"
        elif trust >= 50:
            trust_color = "#B8860B"
            trust_bar   = "#D4A017"
        else:
            trust_color = "#C0392B"
            trust_bar   = "#E74C3C"

        tc, ac = st.columns([2, 3])
        with tc:
            st.markdown(
                f'<div class="vai-trust-block">'
                f'<div class="vai-trust-label">Trust Score</div>'
                f'<div class="vai-trust-score" style="color:{trust_color}">{trust}%</div>'
                f'<div class="vai-trust-sub">'
                f'{summary["correct_count"]} verified out of {summary["total_claims"]} total claims'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="height:6px;background:#EAECEF;border-radius:3px;margin-top:0.5rem;">'
                f'<div style="height:6px;width:{trust}%;background:{trust_bar};'
                f'border-radius:3px;transition:width 0.4s ease"></div></div>',
                unsafe_allow_html=True,
            )
        with ac:
            st.markdown(
                f'<div class="vai-trust-block">'
                f'<div class="vai-trust-label">Accuracy Rate <span style="font-weight:400;letter-spacing:0;'
                f'text-transform:none;font-size:0.75rem">(excl. unverifiable)</span></div>'
                f'<div class="vai-trust-score" style="color:{trust_color}">'
                f'{summary["accuracy_rate"]}%</div>'
                f'<div class="vai-trust-sub">'
                f'High-confidence checks: {summary["high_confidence_count"]}'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        # ── Flagged issues ────────────────────────────────────────────────────
        if summary["issues"]:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p class="vai-section-header">Flagged Issues</p>', unsafe_allow_html=True)

            for r in summary["issues"]:
                if r["verdict"] == "INCORRECT":
                    source_line = ""
                    if r.get("source_says"):
                        source_line += (
                            f'<div class="vai-issue-source">'
                            f'<strong>Source says:</strong> {r["source_says"]}</div>'
                        )
                    if r.get("citation"):
                        source_line += (
                            f'<div class="vai-cite">— {r["citation"]}</div>'
                        )
                    st.markdown(
                        f'<div class="vai-issue-incorrect">'
                        f'<div class="vai-issue-claim">{r["claim"]}</div>'
                        f'{source_line}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                else:  # UNVERIFIABLE
                    cite_line = ""
                    if r.get("citation"):
                        cite_line = f'<div class="vai-cite">Closest source: {r["citation"]}</div>'
                    st.markdown(
                        f'<div class="vai-issue-unverifiable">'
                        f'<div class="vai-issue-claim">{r["claim"]}</div>'
                        f'<div class="vai-issue-meta">No supporting source material found in uploaded documents.</div>'
                        f'{cite_line}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        # ── All claims ────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="vai-section-header">All Claims</p>', unsafe_allow_html=True)

        BADGE = {
            "CORRECT":      ('<span class="vai-badge vai-badge-verified">VERIFIED</span>',   ""),
            "INCORRECT":    ('<span class="vai-badge vai-badge-flagged">FLAGGED</span>',     ""),
            "UNVERIFIABLE": ('<span class="vai-badge vai-badge-unverified">UNVERIFIED</span>', ""),
        }

        for r in summary["all_results"]:
            badge_html, _ = BADGE.get(r["verdict"], ('<span class="vai-badge">?</span>', ""))
            conf      = r.get("confidence", "")
            conf_tag  = f'<span class="vai-conf-tag">{conf}</span>' if conf else ""
            citation  = r.get("citation") or ""
            expl      = r.get("explanation") or ""
            sub_parts = []
            if citation: sub_parts.append(f'<span class="vai-cite">{citation}</span>')
            if expl:     sub_parts.append(expl)
            sub_html  = " &nbsp;·&nbsp; ".join(sub_parts)

            st.markdown(
                f'<div class="vai-card" style="margin-bottom:0.5rem;padding:0.875rem 1.125rem;">'
                f'<div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.35rem">'
                f'{badge_html} {conf_tag}'
                f'<span style="font-size:0.7rem;color:#ADB5BD">#{r.get("claim_number","")}</span>'
                f'</div>'
                f'<div class="vai-claim-text">{r["claim"]}</div>'
                f'<div class="vai-claim-sub">{sub_html}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Export ────────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p class="vai-section-header">Export</p>', unsafe_allow_html=True)

        dl1, dl2, _ = st.columns([1.5, 1.8, 3])
        with dl1:
            st.download_button(
                label="⬇ Download CSV",
                data=st.session_state.csv_data,
                file_name="verifyai_audit.csv",
                mime="text/csv",
            )
        with dl2:
            st.download_button(
                label="⬇ Download Full Report",
                data=st.session_state.report_text,
                file_name="verifyai_audit.txt",
                mime="text/plain",
            )
