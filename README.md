# VerifyAI Hallucination Detector

Upload source documents and an AI-generated report. Automatically detects hallucinations with exact citations.

---

## Features

- **Multi-format source upload** — PDF, DOCX, Excel (.xlsx/.xls)
- **Claim-level verification** — extracts every verifiable claim from the report and checks each one individually
- **Exact citations** — flags hallucinations with file name, page number, and row references
- **Downloadable verification report** — export the full results as a structured report

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Vector store | ChromaDB |
| LLM (claim extraction + verification) | Anthropic Claude API |
| File parsing | pdfplumber, python-docx, openpyxl |
| Language | Python 3.10+ |

---

## Status

**In Development**

---

Built by Shrayan Bhattacharya
