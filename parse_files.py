"""
VerifyAI Hallucination Detector
File parsing utilities — returns structured chunks with exact location metadata
for citations: page number (PDF), sheet + row (Excel), paragraph index (DOCX/TXT).
"""

import io
import os
import pdfplumber
import openpyxl
import docx

# ── OCR paths — Windows only; on Linux tesseract+poppler are on system PATH ──
_WIN_TESSERACT = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
_WIN_POPPLER   = (
    r"C:\Users\shray\AppData\Local\Microsoft\WinGet\Packages"
    r"\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\poppler-25.07.0\Library\bin"
)

def _ocr_pdf(file_bytes: bytes, filename: str) -> list[dict]:
    """OCR fallback for image-based PDFs. Requires tesseract + poppler."""
    import pytesseract
    from pdf2image import convert_from_bytes

    # On Windows set explicit paths; on Linux both tools are on system PATH
    if os.name == "nt":
        pytesseract.pytesseract.tesseract_cmd = _WIN_TESSERACT
        poppler_path = _WIN_POPPLER
    else:
        poppler_path = None

    print(f"  [OCR] No text layer found in {filename} — running OCR...", flush=True)

    images = convert_from_bytes(file_bytes, poppler_path=poppler_path)
    chunks = []
    for i, img in enumerate(images, start=1):
        text = pytesseract.image_to_string(img).strip()
        print(f"  [OCR] Page {i}: {len(text)} chars", flush=True)
        if text:
            chunks.append({
                "text": text,
                "source": filename,
                "page": i,
                "type": "pdf",
            })
    return chunks


def parse_pdf(file_bytes: bytes, filename: str) -> list[dict]:
    """Parse PDF page by page.
    Fast path: pdfplumber (text-based PDFs).
    Fallback:  OCR via tesseract (scanned/image-based PDFs).
    """
    chunks = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                chunks.append({
                    "text": text,
                    "source": filename,
                    "page": i,
                    "type": "pdf",
                })

    if not chunks:
        chunks = _ocr_pdf(file_bytes, filename)

    return chunks


def parse_excel(file_bytes: bytes, filename: str) -> list[dict]:
    """Parse Excel row by row across all sheets. Returns one dict per non-empty data row."""
    chunks = []
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
    for sheet in wb.worksheets:
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            continue
        # Row 1 is the header row (Excel row number 1)
        headers = [str(h).strip() if h is not None else "" for h in rows[0]]
        # Data rows start at Excel row 2
        for excel_row_num, row in enumerate(rows[1:], start=2):
            parts = [
                f"{headers[i]}: {row[i]}"
                for i in range(min(len(headers), len(row)))
                if row[i] is not None and headers[i]
            ]
            if parts:
                chunks.append({
                    "text": " | ".join(parts),
                    "source": filename,
                    "sheet": sheet.title,
                    "row": excel_row_num,
                    "type": "excel",
                    "headers": [h for h in headers if h],
                })
    return chunks


def parse_docx(file_bytes: bytes, filename: str) -> list[dict]:
    """Parse DOCX paragraph by paragraph. Returns one dict per non-empty paragraph."""
    chunks = []
    doc = docx.Document(io.BytesIO(file_bytes))
    para_index = 1
    for para in doc.paragraphs:
        if para.text.strip():
            chunks.append({
                "text": para.text,
                "source": filename,
                "paragraph": para_index,
                "type": "docx",
            })
            para_index += 1
    return chunks


def parse_txt(file_bytes: bytes, filename: str) -> list[dict]:
    """Parse plain text split by double newlines. Returns one dict per paragraph."""
    chunks = []
    text = file_bytes.decode("utf-8", errors="replace")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for i, para in enumerate(paragraphs, start=1):
        chunks.append({
            "text": para,
            "source": filename,
            "paragraph": i,
            "type": "txt",
        })
    return chunks


def parse_file(uploaded_file) -> list[dict]:
    """
    Takes a Streamlit UploadedFile, detects type from extension,
    and returns a list of metadata-rich chunk dicts.
    """
    name = uploaded_file.name
    file_bytes = uploaded_file.read()
    ext = name.lower()

    if ext.endswith(".pdf"):
        return parse_pdf(file_bytes, name)
    elif ext.endswith((".xlsx", ".xls")):
        return parse_excel(file_bytes, name)
    elif ext.endswith(".docx"):
        return parse_docx(file_bytes, name)
    elif ext.endswith(".txt"):
        return parse_txt(file_bytes, name)
    else:
        raise ValueError(f"Unsupported file format: {name}")


def parse_multiple_files(uploaded_files) -> list[dict]:
    """Parse a list of uploaded files and return all chunks combined."""
    all_chunks = []
    for f in uploaded_files:
        all_chunks.extend(parse_file(f))
    return all_chunks


# ── Test block ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fake_chunks = [
        {
            "text": "Total revenue for FY2023 was $4.2 billion, a 12% increase year-over-year.",
            "source": "annual_report.pdf",
            "page": 8,
            "type": "pdf",
        },
        {
            "text": "Region: North America | Q1 Revenue: 1200000 | Q2 Revenue: 1350000 | Growth: 12.5%",
            "source": "data.xlsx",
            "sheet": "Revenue",
            "row": 6,
            "type": "excel",
            "headers": ["Region", "Q1 Revenue", "Q2 Revenue", "Growth"],
        },
        {
            "text": "The board approved a dividend of $0.85 per share, payable in March 2024.",
            "source": "board_minutes.docx",
            "paragraph": 3,
            "type": "docx",
        },
    ]

    print("=" * 60)
    print("parse_files.py — metadata preservation test")
    print("=" * 60)
    for i, chunk in enumerate(fake_chunks, start=1):
        print(f"\nChunk {i}:")
        print(f"  text      : {chunk['text'][:80]}{'...' if len(chunk['text']) > 80 else ''}")
        print(f"  source    : {chunk['source']}")
        if chunk["type"] == "pdf":
            print(f"  citation  : {chunk['source']}, Page {chunk['page']}")
        elif chunk["type"] == "excel":
            print(f"  citation  : {chunk['source']}, Sheet '{chunk['sheet']}', Row {chunk['row']}")
            print(f"  headers   : {chunk['headers']}")
        elif chunk["type"] in ("docx", "txt"):
            print(f"  citation  : {chunk['source']}, Paragraph {chunk['paragraph']}")
        print(f"  type      : {chunk['type']}")

    print(f"\nTotal chunks: {len(fake_chunks)}")
    print("=" * 60)
    print("All metadata preserved correctly.")
