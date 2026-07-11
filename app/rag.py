"""Thin retrieval wrapper around the Chroma vector store built by ingest.py."""

import os
import chromadb
from chromadb.utils import embedding_functions

STORE_DIR = os.path.join(os.path.dirname(__file__), "..", "vectorstore")
COLLECTION_NAME = "value_investing_corpus"

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=STORE_DIR)
        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        try:
            _collection = _client.get_collection(
                name=COLLECTION_NAME, embedding_function=embed_fn
            )
        except Exception:
            # Collection doesn't exist yet — e.g. first run on a fresh
            # deployment where vectorstore/ wasn't committed. Build it now
            # rather than requiring a separate manual `ingest.py` step.
            from app.ingest import build_index

            build_index()
            _collection = _client.get_collection(
                name=COLLECTION_NAME, embedding_function=embed_fn
            )
    return _collection


def retrieve(query: str, company_filter: str | None = None, k: int = 4) -> list[dict]:
    """Retrieve the top-k most relevant chunks for a query.

    Args:
        query: the user's natural-language question.
        company_filter: optional company display name (e.g. "Titan Company")
            to restrict retrieval to a single company's filing.
        k: number of chunks to return.

    Returns:
        List of {text, company, section, source_file, distance} dicts,
        ordered by relevance (lowest distance first).
    """
    collection = _get_collection()
    where = {"company": company_filter} if company_filter else None
    results = collection.query(query_texts=[query], n_results=k, where=where)

    chunks = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, dists):
        chunks.append(
            {
                "text": doc,
                "company": meta.get("company"),
                "section": meta.get("section"),
                "source_file": meta.get("source_file"),
                "distance": dist,
            }
        )
    return chunks
