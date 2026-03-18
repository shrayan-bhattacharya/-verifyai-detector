"""
VerifyAI Hallucination Detector
Chunking + ChromaDB embedding with full metadata inheritance.
Every chunk carries exact location metadata (source, page, row, sheet)
so that search results can be turned directly into citations.
"""

import tempfile
import uuid
import chromadb


def chunk_with_metadata(parsed_blocks: list[dict], chunk_size: int = 500, chunk_overlap: int = 50) -> list[dict]:
    """
    Splits parsed blocks into ChromaDB-ready chunks.
    Short blocks (< chunk_size) pass through as a single chunk.
    Long blocks are split with overlap; every sub-chunk inherits all parent metadata.
    Each chunk gets a unique chunk_id.
    """
    chunks = []

    for block in parsed_blocks:
        text = block["text"]

        if len(text) <= chunk_size:
            chunk = {**block, "chunk_id": str(uuid.uuid4()), "chunk_part": "1 of 1"}
            chunks.append(chunk)
        else:
            # Split with overlap
            parts = []
            start = 0
            while start < len(text):
                end = start + chunk_size
                parts.append(text[start:end])
                if end >= len(text):
                    break
                start += chunk_size - chunk_overlap

            total = len(parts)
            for i, part_text in enumerate(parts, start=1):
                chunk = {
                    **block,
                    "text": part_text,
                    "chunk_id": str(uuid.uuid4()),
                    "chunk_part": f"{i} of {total}",
                }
                chunks.append(chunk)

    return chunks


def create_vector_store(chunks: list[dict], collection_name: str = "sources"):
    """
    Embeds all chunks into a ChromaDB PersistentClient.
    All metadata fields are preserved; lists are converted to comma-separated strings
    to satisfy ChromaDB's scalar-only metadata requirement.
    Returns (collection, chunks).
    """
    client = chromadb.PersistentClient(path=tempfile.mkdtemp())

    # Fresh collection every time
    existing = [c.name for c in client.list_collections()]
    if collection_name in existing:
        client.delete_collection(collection_name)
    collection = client.create_collection(collection_name)

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(chunk["chunk_id"])
        documents.append(chunk["text"])

        # Build metadata dict — exclude "text" and "chunk_id", coerce lists → strings
        meta = {}
        for k, v in chunk.items():
            if k in ("text", "chunk_id"):
                continue
            if isinstance(v, list):
                meta[k] = ", ".join(str(x) for x in v)
            elif v is None:
                meta[k] = ""
            else:
                meta[k] = v
        metadatas.append(meta)

    if not ids:
        raise ValueError("No chunks to embed — the parsed documents may be empty or unreadable.")
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return collection, chunks


def search_sources(collection, query: str, top_k: int = 5) -> list[dict]:
    """
    Semantic search over the ChromaDB collection.
    Returns top_k results sorted by distance (closest first),
    each with full metadata and distance score.
    """
    results = collection.query(query_texts=[query], n_results=top_k)

    hits = []
    for i in range(len(results["ids"][0])):
        hit = {
            "text": results["documents"][0][i],
            "distance": round(results["distances"][0][i], 4),
            **results["metadatas"][0][i],
        }
        hits.append(hit)

    hits.sort(key=lambda x: x["distance"])
    return hits


# ── Test block ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fake_blocks = [
        {
            "text": "Dollar General Corporation reported total revenue of $34.2 billion for fiscal year 2021. The company operated 18,130 stores across 47 states.",
            "source": "dg_annual_report.pdf",
            "page": 8,
            "type": "pdf",
        },
        {
            "text": "Revenue: $34.2B | Stores: 18130 | States: 47 | Employees: 163000",
            "source": "dg_financials.xlsx",
            "sheet": "Summary",
            "row": 2,
            "type": "excel",
            "headers": ["Revenue", "Stores", "States", "Employees"],
        },
        {
            "text": "The company opened 1,050 new stores during the fiscal year while remodeling 1,750 existing locations. Dollar General's selling square footage totaled approximately 156 million square feet.",
            "source": "dg_annual_report.pdf",
            "page": 12,
            "type": "pdf",
        },
    ]

    print("=" * 65)
    print("chunk_and_embed.py — chunking + embedding test")
    print("=" * 65)

    chunks = chunk_with_metadata(fake_blocks)
    print(f"\nInput blocks : {len(fake_blocks)}")
    print(f"Output chunks: {len(chunks)}")
    for c in chunks:
        print(f"  [{c['chunk_part']}] {c['source']}", end="")
        if c.get("page"):
            print(f", Page {c['page']}", end="")
        if c.get("sheet"):
            print(f", Sheet '{c['sheet']}', Row {c['row']}", end="")
        print(f" — \"{c['text'][:60]}...\"" if len(c["text"]) > 60 else f" — \"{c['text']}\"")

    print("\nBuilding vector store...", end=" ", flush=True)
    collection, _ = create_vector_store(chunks)
    print("done.")

    queries = [
        "How many stores does Dollar General operate?",
        "What was the total revenue?",
    ]

    for query in queries:
        print(f"\n{'-' * 65}")
        print(f"Query: \"{query}\"")
        print(f"{'-' * 65}")
        results = search_sources(collection, query, top_k=3)
        for rank, hit in enumerate(results, start=1):
            print(f"\n  Result #{rank}  (distance: {hit['distance']})")
            print(f"  text     : {hit['text'][:80]}{'...' if len(hit['text']) > 80 else ''}")
            print(f"  source   : {hit['source']}")
            if hit.get("page"):
                print(f"  citation : {hit['source']}, Page {hit['page']}")
            elif hit.get("sheet"):
                print(f"  citation : {hit['source']}, Sheet '{hit['sheet']}', Row {hit['row']}")
            print(f"  type     : {hit['type']}  |  chunk_part: {hit['chunk_part']}")

    print(f"\n{'=' * 65}")
    print("Metadata preserved end-to-end through chunking and retrieval.")
