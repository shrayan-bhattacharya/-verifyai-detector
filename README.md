# VerifyAI Hallucination Detector

> Upload source documents. Paste an AI-generated report. Get a claim-by-claim hallucination analysis with exact citations.

---

## What It Does

AI-generated reports often contain hallucinations — facts that sound plausible but are fabricated or misrepresented. **VerifyAI Hallucination Detector** solves this by:

1. **Parsing your source documents** — supports PDF, DOCX, and Excel (.xlsx/.xls)
2. **Extracting every verifiable claim** from the AI report using Claude
3. **Checking each claim** against the source documents via semantic retrieval (ChromaDB)
4. **Returning a verdict** per claim: `SUPPORTED`, `CONTRADICTED`, or `UNVERIFIABLE`
5. **Citing the exact source** — file name, page number, and row reference for every finding
6. **Generating a downloadable report** — export the full verification results

---

## Features

| Feature | Details |
|---|---|
| Multi-format upload | PDF, DOCX, Excel (.xlsx / .xls) |
| Claim-level granularity | Every verifiable sentence checked individually |
| Exact citations | File name + page number + row reference per claim |
| Verdict system | `SUPPORTED` / `CONTRADICTED` / `UNVERIFIABLE` |
| Downloadable report | Export full hallucination report |
| Semantic retrieval | ChromaDB + sentence embeddings for accurate matching |

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Vector store | ChromaDB (`all-MiniLM-L6-v2`) |
| LLM — claim extraction + verification | Anthropic Claude API |
| File parsing | pdfplumber, python-docx, openpyxl |
| Language | Python 3.10+ |

---

## Project Structure

```
verifyai-detector/
├── app.py                  # Streamlit UI
├── parse_files.py          # PDF, DOCX, Excel parsers with page/row metadata
├── chunk_and_embed.py      # Chunking + ChromaDB embedding with rich metadata
├── claim_extractor.py      # Claude-powered claim extraction from AI reports
├── claim_verifier.py       # Per-claim verification against source chunks
├── report_generator.py     # Hallucination report assembly + export
├── requirements.txt
├── .gitignore
└── .env                    # ANTHROPIC_API_KEY (not committed)
```

---

## How to Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/shrayan-bhattacharya/-verifyai-detector.git
cd verifyai-detector
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API key** — create a `.env` file:
```
ANTHROPIC_API_KEY=your-key-here
```

**4. Run the app**
```bash
streamlit run app.py
```

---

## Part of the VerifyAI Suite

| Project | Description |
|---|---|
| [AI Eval Toolkit](https://github.com/shrayan-bhattacharya/ai-eval-toolkit) | LLM answer evaluation with automated scoring and hallucination detection |
| [VerifyAI RAG](https://github.com/shrayan-bhattacharya/verifyai-rag) | Document QA chatbot with per-answer verification |
| **VerifyAI Hallucination Detector** | Claim-level hallucination analysis with exact source citations ← *you are here* |

---

## Status

**In Development** — core pipeline under active construction.

---

Built by [Shrayan Bhattacharya](https://github.com/shrayan-bhattacharya)
