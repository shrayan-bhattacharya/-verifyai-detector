"""
VerifyAI Hallucination Detector
Report generator — compiles claim verification results into a structured
summary, a human-readable text report, and a downloadable CSV.
"""

import csv
import io
from datetime import datetime


# ── 1. Summary ────────────────────────────────────────────────────────────────

def generate_report_summary(verification_results: list[dict]) -> dict:
    """
    Aggregates verification results into a summary dictionary.
    Returns counts, accuracy/trust scores, issues list, and sorted full results.
    """
    total     = len(verification_results)
    correct   = [r for r in verification_results if r["verdict"] == "CORRECT"]
    incorrect = [r for r in verification_results if r["verdict"] == "INCORRECT"]
    unverif   = [r for r in verification_results if r["verdict"] == "UNVERIFIABLE"]
    high_conf = [r for r in verification_results if r.get("confidence") == "HIGH"]

    decidable = len(correct) + len(incorrect)
    accuracy_rate = round(len(correct) / decidable * 100, 1) if decidable else 0.0
    trust_score   = round(len(correct) / total * 100, 1) if total else 0.0

    issues = incorrect + unverif  # INCORRECT first, then UNVERIFIABLE

    all_results_sorted = incorrect + unverif + correct

    return {
        "total_claims":        total,
        "correct_count":       len(correct),
        "incorrect_count":     len(incorrect),
        "unverifiable_count":  len(unverif),
        "accuracy_rate":       accuracy_rate,
        "trust_score":         trust_score,
        "high_confidence_count": len(high_conf),
        "issues":              issues,
        "all_results":         all_results_sorted,
    }


# ── 2. Formatted text report ──────────────────────────────────────────────────

def format_report_text(summary: dict) -> str:
    """
    Renders the summary as a professional plain-text report string.
    """
    lines = []
    width = 70

    def rule(char="="):
        lines.append(char * width)

    def section(title):
        lines.append("")
        rule("-")
        lines.append(f"  {title}")
        rule("-")

    # Header
    rule()
    lines.append("  VERIFYAI HALLUCINATION REPORT".center(width))
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(width))
    rule()

    # Overview
    section("OVERVIEW")
    t = summary["total_claims"]
    c = summary["correct_count"]
    i = summary["incorrect_count"]
    u = summary["unverifiable_count"]
    lines.append(f"  Claims Analyzed  : {t}")
    lines.append(f"  Verified Correct : {c}  ({round(c/t*100,1) if t else 0}%)")
    lines.append(f"  Incorrect        : {i}  ({round(i/t*100,1) if t else 0}%)")
    lines.append(f"  Unverifiable     : {u}  ({round(u/t*100,1) if t else 0}%)")
    lines.append(f"  Accuracy Rate    : {summary['accuracy_rate']}%  (excl. unverifiable)")
    lines.append(f"  Trust Score      : {summary['trust_score']}%  (correct / total)")
    lines.append(f"  High-Conf Checks : {summary['high_confidence_count']}")

    # Issues
    if summary["issues"]:
        section("ISSUES REQUIRING ATTENTION")
        for r in summary["issues"]:
            tag = f"[{r['verdict']}]"
            claim_short = (r["claim"][:90] + "...") if len(r["claim"]) > 90 else r["claim"]
            lines.append(f"\n  {tag} Claim: \"{claim_short}\"")
            if r["verdict"] == "INCORRECT" and r.get("source_says"):
                lines.append(f"    Source says : {r['source_says']}")
                lines.append(f"    Citation    : {r.get('citation') or 'N/A'}")
            elif r["verdict"] == "UNVERIFIABLE":
                lines.append(f"    No supporting source found in uploaded documents.")
                if r.get("citation"):
                    lines.append(f"    Closest source: {r['citation']}")
    else:
        section("ISSUES REQUIRING ATTENTION")
        lines.append("  None — all claims verified against source documents.")

    # Full results
    section("FULL VERIFICATION RESULTS")
    verdict_order = {"INCORRECT": 1, "UNVERIFIABLE": 2, "CORRECT": 3}
    for r in summary["all_results"]:
        num = r.get("claim_number", "?")
        verdict    = r["verdict"]
        confidence = r.get("confidence", "N/A")
        citation   = r.get("citation") or "N/A"
        explanation= r.get("explanation", "")
        claim_short = (r["claim"][:85] + "...") if len(r["claim"]) > 85 else r["claim"]

        lines.append(f"\n  Claim {num:>2}  [{verdict}]  confidence: {confidence}")
        lines.append(f"    Text       : {claim_short}")
        lines.append(f"    Citation   : {citation}")
        lines.append(f"    Explanation: {explanation}")

    lines.append("")
    rule()
    lines.append("  End of Report — VerifyAI Hallucination Detector".center(width))
    rule()

    return "\n".join(lines)


# ── 3. CSV report ─────────────────────────────────────────────────────────────

def generate_csv_report(verification_results: list[dict]) -> str:
    """
    Returns a CSV-formatted string with one row per verified claim.
    Columns: Claim Number, Claim Text, Verdict, Confidence, Citation,
             Explanation, Source Says
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    writer.writerow([
        "Claim Number", "Claim Text", "Verdict", "Confidence",
        "Citation", "Explanation", "Source Says",
    ])

    for r in sorted(verification_results, key=lambda x: x.get("claim_number", 0)):
        writer.writerow([
            r.get("claim_number", ""),
            r.get("claim", ""),
            r.get("verdict", ""),
            r.get("confidence", ""),
            r.get("citation") or "",
            r.get("explanation", ""),
            r.get("source_says") or "",
        ])

    return output.getvalue()


# ── Test block ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.dirname(__file__))

    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

    from chunk_and_embed import chunk_with_metadata, create_vector_store
    from claim_extractor import extract_claims
    from claim_verifier import verify_all_claims

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not found in .env")

    # Same source blocks and test report as previous steps
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

    TEST_REPORT = (
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

    print("Running full pipeline...", flush=True)

    chunks = chunk_with_metadata(source_blocks)
    collection, _ = create_vector_store(chunks)
    print(f"  Embedded {len(chunks)} chunks.")

    claims = extract_claims(TEST_REPORT, api_key)
    print(f"  Extracted {len(claims)} claims.")

    results = verify_all_claims(claims, collection, api_key)
    print(f"  Verified {len(results)} claims.")

    # Generate all report formats
    summary  = generate_report_summary(results)
    report   = format_report_text(summary)
    csv_data = generate_csv_report(results)

    # Print text report
    print("\n" + report)

    # Print CSV
    print("\n" + "=" * 70)
    print("  CSV OUTPUT (downloadable report)")
    print("=" * 70)
    print(csv_data)

    # Print summary stats
    print("=" * 70)
    print("  SUMMARY STATS")
    print("=" * 70)
    print(f"  Total claims     : {summary['total_claims']}")
    print(f"  Correct          : {summary['correct_count']}")
    print(f"  Incorrect        : {summary['incorrect_count']}")
    print(f"  Unverifiable     : {summary['unverifiable_count']}")
    print(f"  Accuracy rate    : {summary['accuracy_rate']}%")
    print(f"  Trust score      : {summary['trust_score']}%")
    print(f"  High-conf checks : {summary['high_confidence_count']}")
    print("=" * 70)
