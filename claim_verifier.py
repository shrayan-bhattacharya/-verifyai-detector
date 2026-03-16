"""
VerifyAI Hallucination Detector
Claim verifier — for each extracted claim, retrieves relevant source
chunks from ChromaDB and asks Claude to return a CORRECT / INCORRECT /
UNVERIFIABLE verdict with an exact citation.
"""

import os
import re
from dotenv import load_dotenv
import anthropic
from chunk_and_embed import search_sources

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SYSTEM_PROMPT = """\
You are a precise fact-checking system. Compare the CLAIM against the SOURCE material provided.

Rules:
- If the claim is fully supported by the sources, verdict is CORRECT
- If the claim contradicts the sources (wrong numbers, wrong facts, wrong dates), verdict is INCORRECT. State what the source actually says.
- If the sources are somewhat related but don't contain enough information to confirm or deny the claim, verdict is UNVERIFIABLE
- Always cite the specific source (filename, page/row) that supports your verdict
- Be strict — if a number is even slightly different, it's INCORRECT

Respond in this exact format:
VERDICT: [CORRECT/INCORRECT/UNVERIFIABLE]
CITATION: [source filename, page/sheet/row reference]
EXPLANATION: [one clear sentence explaining why]
SOURCE_SAYS: [what the source actually states, if relevant — quote the key part]"""


def _build_citation(meta: dict) -> str:
    """Format a chunk's metadata into a human-readable citation string."""
    source = meta.get("source", "unknown")
    if meta.get("type") == "pdf" and meta.get("page"):
        return f"{source}, Page {meta['page']}"
    if meta.get("type") == "excel" and meta.get("sheet"):
        return f"{source}, Sheet '{meta['sheet']}', Row {meta['row']}"
    if meta.get("type") in ("docx", "txt") and meta.get("paragraph"):
        return f"{source}, Paragraph {meta['paragraph']}"
    return source


def _confidence(distance: float | None) -> str:
    """Map best-chunk distance to a human-readable confidence label."""
    if distance is None:
        return "NONE"
    if distance < 0.5:
        return "HIGH"
    if distance < 0.8:
        return "MEDIUM"
    return "LOW"


def verify_claim(
    claim_text: str,
    collection,
    api_key: str,
    top_k: int = 7,
    distance_threshold: float = 1.2,
) -> dict:
    """
    Verifies a single claim against the ChromaDB source collection.
    Returns a dict with verdict, citation, explanation, and source_says.
    """
    hits = search_sources(collection, claim_text, top_k=top_k)
    relevant = [h for h in hits if h["distance"] <= distance_threshold]

    if not relevant:
        return {
            "verdict": "UNVERIFIABLE",
            "claim": claim_text,
            "explanation": "No relevant source material found.",
            "citation": None,
            "source_says": None,
            "distance": None,
            "confidence": "NONE",
            "sources_checked": 0,
        }

    # Build context block with labelled citations
    context_parts = []
    for h in relevant:
        citation = _build_citation(h)
        context_parts.append(f"SOURCE [{citation}]: {h['text']}")
    context = "\n\n".join(context_parts)

    user_prompt = (
        f"CLAIM: {claim_text}\n\n"
        f"SOURCE MATERIAL:\n{context}"
    )

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()

    def _extract(label: str) -> str:
        match = re.search(rf"^{label}:\s*(.+)$", raw, re.MULTILINE | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    best_distance = relevant[0]["distance"]
    return {
        "verdict":         _extract("VERDICT").upper(),
        "claim":           claim_text,
        "citation":        _extract("CITATION"),
        "explanation":     _extract("EXPLANATION"),
        "source_says":     _extract("SOURCE_SAYS"),
        "distance":        best_distance,
        "confidence":      _confidence(best_distance),
        "sources_checked": len(relevant),
    }


def verify_all_claims(claims_list: list[dict], collection, api_key: str) -> list[dict]:
    """
    Verifies every claim in claims_list against the source collection.
    Each item in claims_list must have 'claim_number' and 'claim_text'.
    Prints progress and returns a list of verification result dicts.
    """
    total = len(claims_list)
    results = []
    for item in claims_list:
        print(f"  Verifying claim {item['claim_number']} of {total}...", flush=True)
        result = verify_claim(item["claim_text"], collection, api_key)
        result["claim_number"] = item["claim_number"]
        results.append(result)
    return results


# ── Test block ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(__file__))

    from chunk_and_embed import chunk_with_metadata, create_vector_store
    from claim_extractor import extract_claims

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not found in .env")

    # ── 1. Simulated source documents ─────────────────────────────────────────
    source_blocks = [
        {
            "text": (
                "Dollar General Corporation reported total revenue of $34.2 billion "
                "for fiscal year 2021, representing a 1.4% increase from the prior year. "
                "The company operated 18,130 stores across 47 states as of the end of fiscal 2021."
            ),
            "source": "dg_annual_report.pdf", "page": 8, "type": "pdf",
        },
        {
            "text": (
                "Net income for the year was approximately $2.4 billion. "
                "The company opened 1,050 new stores during the fiscal year "
                "while remodeling 1,750 existing locations."
            ),
            "source": "dg_annual_report.pdf", "page": 12, "type": "pdf",
        },
        {
            "text": (
                "The company employed roughly 163,000 full-time and part-time employees. "
                "Same-store sales decreased 2.8% compared to fiscal 2020. "
                "Gross profit margin was 31.6% of net sales."
            ),
            "source": "dg_annual_report.pdf", "page": 15, "type": "pdf",
        },
        {
            "text": "Revenue: $34.2B | Stores: 18130 | New Stores: 1050 | Remodels: 1750 | Employees: 163000",
            "source": "dg_financials.xlsx", "sheet": "Summary", "row": 2,
            "type": "excel", "headers": ["Revenue", "Stores", "New Stores", "Remodels", "Employees"],
        },
    ]

    # ── 2. Test report — contains CORRECT, INCORRECT, and UNVERIFIABLE claims ─
    TEST_REPORT = (
        "Dollar General Corporation reported total revenue of $34.2 billion for fiscal year 2021, "
        "a 1.4% increase from the prior year. "                          # CORRECT
        "The company operated 18,130 stores across 48 states. "          # INCORRECT (source: 47 states)
        "Net income reached $2.8 billion for the fiscal year. "          # INCORRECT (source: $2.4B)
        "Dollar General opened 1,050 new stores and remodeled 1,750 locations. "  # CORRECT
        "The company employed approximately 163,000 workers. "           # CORRECT
        "Same-store sales decreased 2.8% versus fiscal 2020. "          # CORRECT
        "Gross profit margin was 31.6%. "                                 # CORRECT
        "CEO Todd Vasos announced plans to expand into Canada by 2023."  # UNVERIFIABLE
    )

    VERDICT_ICON = {"CORRECT": "[+]", "INCORRECT": "[!]", "UNVERIFIABLE": "[?]"}

    print("=" * 70)
    print("claim_verifier.py — end-to-end pipeline test")
    print("=" * 70)

    # ── 3. Chunk + embed ──────────────────────────────────────────────────────
    print("\n[1/3] Chunking and embedding source documents...", flush=True)
    chunks = chunk_with_metadata(source_blocks)
    collection, _ = create_vector_store(chunks)
    print(f"      {len(chunks)} chunks stored in ChromaDB.")

    # ── 4. Extract claims ─────────────────────────────────────────────────────
    print("\n[2/3] Extracting claims from report...", flush=True)
    claims = extract_claims(TEST_REPORT, api_key)
    print(f"      {len(claims)} claims extracted.")

    # ── 5. Verify all claims ──────────────────────────────────────────────────
    print(f"\n[3/3] Verifying {len(claims)} claims against source documents...")
    results = verify_all_claims(claims, collection, api_key)

    # ── 6. Print results ──────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)

    for r in results:
        icon = VERDICT_ICON.get(r["verdict"], "?")
        print(f"\nClaim {r['claim_number']:>2}  [{icon} {r['verdict']}]")
        print(f"  Claim      : {r['claim']}")
        print(f"  Citation   : {r['citation'] or 'N/A'}")
        print(f"  Explanation: {r['explanation']}")
        if r["source_says"]:
            print(f"  Source says: {r['source_says']}")
        print(f"  Confidence : {r.get('confidence', 'N/A')}  |  Distance: {r['distance']}  |  Chunks used: {r['sources_checked']}")

    # ── 7. Summary ────────────────────────────────────────────────────────────
    correct      = sum(1 for r in results if r["verdict"] == "CORRECT")
    incorrect    = sum(1 for r in results if r["verdict"] == "INCORRECT")
    unverifiable = sum(1 for r in results if r["verdict"] == "UNVERIFIABLE")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Total claims     : {len(results)}")
    print(f"  [+] CORRECT      : {correct}")
    print(f"  [!] INCORRECT    : {incorrect}")
    print(f"  [?] UNVERIFIABLE : {unverifiable}")
    print("=" * 70)
