"""
Builds the RAG vector store from the markdown corpus in data/annual_reports/.

Run once (and re-run any time you add/update source documents):
    python app/ingest.py

Chunking strategy: split each markdown file on "## " headings, so each chunk
is a coherent section (e.g. "Competitive Moat", "Risks") rather than an
arbitrary character window. This keeps retrieved context readable and
citeable in the UI.
"""

import os
import re
import glob

import chromadb
from chromadb.utils import embedding_functions

CORPUS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "annual_reports")
STORE_DIR = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
COLLECTION_NAME = "value_investing_corpus"


def chunk_markdown(text: str, source: str) -> list[dict]:
    """Split a markdown doc into (heading, content) chunks."""
    # Keep the H1 title as context prefix for every chunk. Titles are of the
    # form "Company Name (TICKER.NS) — Sample Corpus Excerpt"; strip the
    # " — Sample Corpus Excerpt" suffix so the company metadata used for
    # filtering is just "Company Name (TICKER.NS)".
    title_match = re.match(r"#\s+(.+)", text)
    title = title_match.group(1).strip() if title_match else source
    title = re.split(r"\s+—\s+", title)[0].strip()

    sections = re.split(r"\n(?=## )", text)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section.startswith("## "):
            # Skip the bare H1/title/note preamble before the first "## " heading.
            continue
        heading_match = re.match(r"##\s+(.+)", section)
        heading = heading_match.group(1).strip() if heading_match else "Overview"
        chunks.append(
            {
                "text": f"[{title} — {heading}]\n{section}",
                "company": title,
                "section": heading,
                "source_file": source,
            }
        )
    return chunks


def build_index():
    os.makedirs(STORE_DIR, exist_ok=True)
    client = chromadb.PersistentClient(path=STORE_DIR)

    # Local, free sentence-transformers embedding model — no external API
    # call needed for embeddings (keeps the RAG step independent of the
    # Anthropic API budget/rate limits).
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Fresh build each time for simplicity in a demo app.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME, embedding_function=embed_fn
    )

    all_chunks = []
    for path in sorted(glob.glob(os.path.join(CORPUS_DIR, "*.md"))):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        source = os.path.basename(path)
        all_chunks.extend(chunk_markdown(text, source))

    if not all_chunks:
        print("No source documents found in", CORPUS_DIR)
        return

    collection.add(
        ids=[f"{c['source_file']}::{c['section']}::{i}" for i, c in enumerate(all_chunks)],
        documents=[c["text"] for c in all_chunks],
        metadatas=[
            {"company": c["company"], "section": c["section"], "source_file": c["source_file"]}
            for c in all_chunks
        ],
    )
    print(f"Indexed {len(all_chunks)} chunks from {len(set(c['source_file'] for c in all_chunks))} documents into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    build_index()
