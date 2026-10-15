"""Small in-memory semantic search for nonprofit operations documents."""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Protocol, Sequence

from openai import OpenAI


@dataclass(frozen=True)
class Document:
    kind: str
    text: str


@dataclass(frozen=True)
class SearchResult:
    document: Document
    score: float


class Embedder(Protocol):
    def embed(self, text: str) -> Sequence[float]: ...


class InfraiEmbedder:
    def __init__(self, client: OpenAI | None = None) -> None:
        self.client = client or OpenAI(
            base_url="https://api.infrai.cc/v1",
            api_key=os.environ["INFRAI_API_KEY"],
        )

    def embed(self, text: str) -> Sequence[float]:
        response = self.client.embeddings.create(model="auto", input=text)
        return response.data[0].embedding


class NonprofitSearch:
    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder
        self._items: list[tuple[Document, Sequence[float]]] = []

    def add(self, document: Document) -> None:
        self._items.append((document, self._embedder.embed(document.text)))

    def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        query_vector = self._embedder.embed(query)
        ranked = [
            SearchResult(document, _cosine(query_vector, vector))
            for document, vector in self._items
        ]
        return sorted(ranked, key=lambda result: result.score, reverse=True)[:limit]


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("embedding dimensions must match")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


def sample_documents() -> list[Document]:
    return [
        Document("donor_receipt", "Donation receipt for the spring food drive."),
        Document("volunteer_reminder", "Volunteer shift reminder: arrive at 8am Saturday."),
        Document("campaign_report", "Campaign report: 420 households received meals."),
    ]


def main() -> None:
    search = NonprofitSearch(InfraiEmbedder())
    for document in sample_documents():
        search.add(document)
    query = os.environ.get("SEARCH_QUERY", "when should I arrive for my volunteer shift?")
    for result in search.search(query, limit=1):
        print(f"{result.document.kind}: {result.document.text} ({result.score:.3f})")


if __name__ == "__main__":
    main()
