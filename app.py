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
/* ── Base & typography ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* ── Root color tokens ── */
:root {
    --navy:        #1B2A4A;
    --navy-mid:    #243557;
    --navy-light:  #2E4370;
    --accent:      #2E6EA6;
    --accent-light:#3D84C8;
    --success:     #2D8B4E;
    --success-bg:  #EAF6EE;
    --error:       #C0392B;
    --error-bg:    #FBEAEA;
    --warning:     #B8860B;
    --warning-bg:  #FEF9E7;
    --gray-50:     #F8F9FA;
    --gray-100:    #EAECEF;
    --gray-300:    #CED4DA;
    --gray-500:    #6C757D;
    --gray-700:    #495057;
    --gray-900:    #212529;
    --white:       #FFFFFF;
}

/* ── App background ── */
.stApp { background-color: var(--gray-50); }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: var(--white);
    border-right: 1px solid var(--gray-100);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }

/* ── Override Streamlit buttons to navy/blue ── */
.stButton > button {
    background-color: var(--accent) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 1.25rem !important;
    transition: background-color 0.15s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
}
.stButton > button:hover {
    background-color: var(--accent-light) !important;
}
.stButton > button[kind="primary"] {
    background-color: var(--navy) !important;
    font-size: 1rem !important;
    padding: 0.625rem 1.75rem !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: var(--navy-mid) !important;
}

/* ── Download buttons ── */
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

/* ── Progress bar ── */
.stProgress > div > div > div { background-color: var(--accent) !important; }

/* ── Text area ── */
.stTextArea textarea {
    border: 1px solid var(--gray-300) !important;
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    color: var(--gray-900) !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(46,110,166,0.12) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 1.5px dashed var(--gray-300) !important;
    border-radius: 8px !important;
    background: var(--gray-50) !important;
}

/* ── Cards ── */
.vai-card {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.vai-feature-card {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-radius: 10px;
    padding: 1.5rem 1.25rem;
    text-align: center;
    height: 100%;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.vai-feature-icon {
    font-size: 1.75rem;
    margin-bottom: 0.75rem;
}
.vai-feature-title {
    font-weight: 600;
    color: var(--navy);
    font-size: 0.9375rem;
    margin-bottom: 0.4rem;
}
.vai-feature-desc {
    color: var(--gray-500);
    font-size: 0.8125rem;
    line-height: 1.5;
}

/* ── Section headers ── */
.vai-section-header {
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--gray-500);
    margin: 0 0 0.875rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--gray-100);
}

/* ── Metric cards ── */
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
    color: var(--gray-500);
    margin-bottom: 0.3rem;
}
.vai-metric-value {
    font-size: 1.875rem;
    font-weight: 700;
    line-height: 1.1;
}
.vai-metric-navy  { color: var(--navy); }
.vai-metric-green { color: var(--success); }
.vai-metric-red   { color: var(--error); }
.vai-metric-amber { color: var(--warning); }

/* ── Trust score ── */
.vai-trust-block {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-radius: 10px;
    padding: 1.5rem 2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.vai-trust-label {
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--gray-500);
    margin-bottom: 0.25rem;
}
.vai-trust-score {
    font-size: 3rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.vai-trust-sub {
    font-size: 0.8125rem;
    color: var(--gray-500);
    margin-top: 0.35rem;
}

/* ── Issue cards ── */
.vai-issue-incorrect {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-left: 4px solid var(--error);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.vai-issue-unverifiable {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-left: 4px solid var(--warning);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.vai-issue-claim {
    font-size: 0.9375rem;
    font-weight: 500;
    color: var(--gray-900);
    margin-bottom: 0.4rem;
}
.vai-issue-meta {
    font-size: 0.8125rem;
    color: var(--gray-500);
    line-height: 1.5;
}
.vai-issue-source {
    font-size: 0.8125rem;
    color: var(--gray-700);
    margin-top: 0.3rem;
}
.vai-cite {
    font-size: 0.75rem;
    color: var(--accent);
    font-style: italic;
}

/* ── All claims table-style rows ── */
.vai-claim-row {
    background: var(--white);
    border: 1px solid var(--gray-100);
    border-radius: 8px;
    padding: 0.875rem 1.125rem;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.vai-badge {
    display: inline-block;
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    white-space: nowrap;
}
.vai-badge-verified    { background: #D4EDDA; color: #1A5E32; }
.vai-badge-flagged     { background: #FADBD8; color: #7B2020; }
.vai-badge-unverified  { background: #FEF9E7; color: #7D5A00; border: 1px solid #F0D060; }
.vai-conf-tag {
    font-size: 0.6875rem;
    color: var(--gray-500);
    font-weight: 500;
}
.vai-claim-text {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--gray-900);
}
.vai-claim-sub {
    font-size: 0.8rem;
    color: var(--gray-500);
    margin-top: 0.2rem;
    line-height: 1.45;
}

/* ── Logo area ── */
.vai-logo-title {
    font-size: 1.375rem;
    font-weight: 700;
    color: var(--navy);
    letter-spacing: -0.01em;
}
.vai-logo-sub {
    font-size: 0.75rem;
    color: var(--gray-500);
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-top: 0.1rem;
}
.vai-hr { border: none; border-top: 1px solid var(--gray-100); margin: 1rem 0; }

/* ── Status card ── */
.vai-status-card {
    background: var(--success-bg);
    border: 1px solid #A3D9B1;
    border-radius: 8px;
    padding: 0.875rem 1rem;
    font-size: 0.875rem;
    color: var(--success);
    font-weight: 500;
}
.vai-status-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.2rem;
    font-size: 0.8125rem;
    color: var(--gray-700);
}

/* ── Info banner ── */
.vai-info-banner {
    background: #EAF2FA;
    border: 1px solid #BDD7EF;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-size: 0.875rem;
    color: #1B4F72;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Main header ── */
.vai-main-title {
    font-size: 2rem;
    font-weight: 700;
    color: var(--navy);
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
}
.vai-main-sub {
    font-size: 1rem;
    color: var(--gray-500);
    font-weight: 400;
    margin-bottom: 1.75rem;
}

/* ── Export section ── */
.vai-export-row {
    display: flex;
    gap: 0.75rem;
    align-items: center;
}

/* ── Sidebar footer ── */
.vai-sidebar-footer {
    font-size: 0.75rem;
    color: var(--gray-500);
    text-align: center;
    padding: 0.5rem 0;
}
.vai-sidebar-footer a {
    color: var(--accent);
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────────────────────
if "collection"       not in st.session_state: st.session_state.collection       = None
if "chunks_count"     not in st.session_state: st.session_state.chunks_count     = 0
if "files_processed"  not in st.session_state: st.session_state.files_processed  = []
if "audit_results"    not in st.session_state: st.session_state.audit_results    = None
if "audit_summary"    not in st.session_state: st.session_state.audit_summary    = None
if "report_text"      not in st.session_state: st.session_state.report_text      = None
if "csv_data"         not in st.session_state: st.session_state.csv_data         = None
if "chroma_dir"       not in st.session_state: st.session_state.chroma_dir       = tempfile.mkdtemp()

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

        process_btn = st.button("Process Documents", use_container_width=True)

        if process_btn:
            api_key = _get_api_key()
            if not api_key:
                st.error("ANTHROPIC_API_KEY not found.")
            else:
                with st.spinner("Parsing and embedding documents…"):
                    from parse_files import parse_file
                    from chunk_and_embed import chunk_with_metadata, create_vector_store

                    all_blocks = []

                    for uf in uploaded_files:
                        blocks = parse_file(uf)
                        all_blocks.extend(blocks)

                    chunks = chunk_with_metadata(all_blocks)
                    collection, _ = create_vector_store(chunks)

                    st.session_state.collection      = collection
                    st.session_state.chunks_count    = len(chunks)
                    st.session_state.files_processed = [f.name for f in uploaded_files]
                    st.session_state.audit_results   = None  # reset previous audit

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

    # ── Report input ──────────────────────────────────────────────────────────
    report_text = st.text_area(
        "AI-Generated Report",
        value=DG_TEST_REPORT,
        height=250,
        placeholder="Paste the AI-generated report you want to verify…",
        help="Every verifiable factual claim in this text will be checked against your source documents.",
    )

    run_btn = st.button("Run Audit", type="primary", use_container_width=False)

    # ── Run audit pipeline ────────────────────────────────────────────────────
    if run_btn and report_text.strip():
        from claim_extractor  import extract_claims
        from claim_verifier   import verify_all_claims
        from report_generator import generate_report_summary, format_report_text, generate_csv_report

        progress_bar = st.progress(0, text="Extracting claims…")

        claims = extract_claims(report_text, api_key)
        n      = len(claims)
        progress_bar.progress(10, text=f"Extracted {n} claims. Verifying…")

        results = []
        for i, item in enumerate(claims):
            from claim_verifier import verify_claim
            r = verify_claim(item["claim_text"], st.session_state.collection, api_key)
            r["claim_number"] = item["claim_number"]
            results.append(r)
            pct = int(10 + 88 * (i + 1) / n)
            progress_bar.progress(pct, text=f"Verifying claim {i+1} of {n}…")

        progress_bar.progress(100, text="Audit complete.")
        progress_bar.empty()

        summary    = generate_report_summary(results)
        report_out = format_report_text(summary)
        csv_out    = generate_csv_report(results)

        st.session_state.audit_results = results
        st.session_state.audit_summary = summary
        st.session_state.report_text   = report_out
        st.session_state.csv_data      = csv_out

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
