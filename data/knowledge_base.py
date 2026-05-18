"""
knowledge_base.py
─────────────────
In-memory knowledge base with keyword-based search.

WHAT THIS DOES:
- Loads the sample engineering documents into memory
- Scores each document against a search query using keyword overlap
- Returns the top-K most relevant documents

WHY KEYWORD SEARCH (NOT VECTOR SEARCH) FOR THIS PROTOTYPE:
- No Azure AI Search subscription needed to run locally
- Demonstrates the RAG concept without infrastructure dependencies
- Easy to swap out: replace the `search` method with an
  Azure AI Search client call — the interface stays identical

PRODUCTION UPGRADE PATH:
  Step 1: Create an Azure AI Search resource
  Step 2: Create an index with a vector field
  Step 3: Embed documents using Azure OpenAI text-embedding-3-large
  Step 4: Replace `_keyword_score` with vector cosine similarity
  Step 5: Same interface, production-grade semantic retrieval

INTERVIEW TALKING POINT:
  "This prototype uses keyword search to demonstrate the RAG pattern
   without requiring Azure AI Search. In production, I'd index
   engineering standards using Azure OpenAI embeddings and perform
   hybrid search — combining keyword BM25 with semantic vector search
   for maximum recall and precision."
"""

from typing import List, Dict
from data.sample_docs import SAMPLE_DOCUMENTS


class KnowledgeBase:
    """
    Simple in-memory knowledge base with keyword relevance scoring.
    Acts as a stand-in for Azure AI Search in this prototype.
    """

    def __init__(self):
        self.documents = SAMPLE_DOCUMENTS
        print(f"[KnowledgeBase] Loaded {len(self.documents)} engineering documents.")

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Search documents by keyword relevance.

        Args:
            query:  Natural language search query
            top_k:  Number of top results to return

        Returns:
            List of document dicts sorted by relevance score (descending)
        """
        query_tokens = set(query.lower().split())

        scored = []
        for doc in self.documents:
            score = self._keyword_score(query_tokens, doc)
            if score > 0:
                scored.append({
                    "id":      doc["id"],
                    "title":   doc["title"],
                    "source":  doc["source"],
                    "content": doc["content"].strip(),
                    "score":   score,
                })

        # Sort by score descending, return top K
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def _keyword_score(self, query_tokens: set, doc: dict) -> float:
        """
        Score a document against a set of query tokens.

        Scoring logic:
        - Keyword match in `keywords` field:  +2.0 per match  (high signal)
        - Word match in `title`:              +1.5 per match  (medium-high signal)
        - Word match in `content`:            +0.5 per match  (lower signal)
        """
        score = 0.0

        # Check keywords list
        doc_keywords = set(k.lower() for k in doc.get("keywords", []))
        keyword_hits = query_tokens & doc_keywords
        score += len(keyword_hits) * 2.0

        # Check title
        title_tokens = set(doc["title"].lower().split())
        title_hits = query_tokens & title_tokens
        score += len(title_hits) * 1.5

        # Check content (count total occurrences)
        content_lower = doc["content"].lower()
        for token in query_tokens:
            if len(token) > 3:  # Skip short stop words
                score += content_lower.count(token) * 0.5

        return score
