"""
VerifyAI Hallucination Detector
Claim extraction — uses Claude to break an AI-generated report into
individual, self-contained, verifiable factual claims.
"""

import os
import re
from dotenv import load_dotenv
import anthropic

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SYSTEM_PROMPT = """\
You are a precise claim extraction system. Your job is to break down a report into individual, verifiable factual claims.

Rules:
- Extract ONLY factual, verifiable claims (numbers, dates, names, quantities, percentages, specific statements)
- Skip opinions, subjective assessments, recommendations, and transition sentences
- Each claim should be self-contained — understandable without reading the rest of the report
- Preserve the exact numbers and wording from the original report
- Number each claim sequentially

Respond in this exact format, one claim per line:
CLAIM 1: [claim text]
CLAIM 2: [claim text]
CLAIM 3: [claim text]
...

Do NOT include any other text, headers, or explanations."""


def extract_claims(report_text: str, api_key: str) -> list[dict]:
    """
    Sends the report to Claude and parses the response into a list of
    {"claim_number": int, "claim_text": str} dicts.
    """
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Extract all verifiable factual claims from this report:\n\n{report_text}",
            }
        ],
    )

    raw = message.content[0].text.strip()

    claims = []
    for line in raw.splitlines():
        line = line.strip()
        match = re.match(r"^CLAIM\s+(\d+):\s*(.+)$", line, re.IGNORECASE)
        if match:
            claims.append({
                "claim_number": int(match.group(1)),
                "claim_text": match.group(2).strip(),
            })

    return claims


# ── Test block ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    SAMPLE_REPORT = (
        "Dollar General Corporation reported total revenue of $34.2 billion for fiscal year 2021, "
        "representing a 1.4% increase from the prior year. The company operated 18,130 stores across "
        "47 states as of the end of fiscal 2021. Net income was approximately $2.4 billion. During the "
        "year, the company opened 1,050 new stores and remodeled 1,750 existing locations. The company's "
        "strong geographic moat continues to drive competitive advantage. Dollar General employed roughly "
        "163,000 full-time and part-time employees. Same-store sales decreased 2.8% compared to fiscal "
        "2020, which had benefited from pandemic-driven demand. Gross profit margin was 31.6% of net sales. "
        "Management expects continued expansion into rural markets, which remains a strategic priority."
    )

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not found in .env")

    print("=" * 65)
    print("claim_extractor.py -- claim extraction test")
    print("=" * 65)
    print("\nReport snippet:")
    print(f"  \"{SAMPLE_REPORT[:120]}...\"")
    print("\nExtracting claims...\n")

    claims = extract_claims(SAMPLE_REPORT, api_key)

    for claim in claims:
        print(f"  Claim {claim['claim_number']:>2}: {claim['claim_text']}")

    print(f"\nTotal claims extracted: {len(claims)}")
    print("=" * 65)
    print("Opinions/recommendations correctly excluded.")
