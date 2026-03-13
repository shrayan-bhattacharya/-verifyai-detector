# claim_verifier.py
# For each extracted claim, retrieves the most relevant source
# chunks from ChromaDB and asks Claude to verify the claim,
# returning a verdict (SUPPORTED / CONTRADICTED / UNVERIFIABLE)
# plus the exact citation (file, page, row).
