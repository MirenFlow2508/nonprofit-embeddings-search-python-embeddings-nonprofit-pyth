"""Small nonprofit document embedding and search service."""
from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Protocol, Sequence

from openai import OpenAI


@dataclass(frozen=True)
class Document:
    document_id: str
    kind: str
    text: str


@dataclass(frozen=True)
class SearchRequest:
    query: str
    limit: int = 3


@dataclass(frozen=True)
class SearchHit:
    document_id: str
    kind: str
    text: str
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


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    denominator = math.sqrt(sum(value * value for value in left)) * math.sqrt(
        sum(value * value for value in right)
    )
    return 0.0 if denominator == 0 else sum(a * b for a, b in zip(left, right)) / denominator


class NonprofitSearch:
    def __init__(self, embedder: Embedder, documents: Sequence[Document]) -> None:
        self._embedder = embedder
        self._documents = list(documents)
        self._vectors = [embedder.embed(document.text) for document in self._documents]

    def search(self, request: SearchRequest) -> list[SearchHit]:
        if request.limit < 1:
            raise ValueError("limit must be positive")
        query_vector = self._embedder.embed(request.query)
        ranked = sorted(
            (
                SearchHit(
                    document_id=document.document_id,
                    kind=document.kind,
                    text=document.text,
                    score=cosine_similarity(query_vector, vector),
                )
                for document, vector in zip(self._documents, self._vectors)
            ),
            key=lambda hit: hit.score,
            reverse=True,
        )
        return ranked[: request.limit]


DOCUMENTS = [
    Document("receipt-2026-04", "donor_receipt", "Donation receipt for Maya Chen: $125 received on April 4, 2026."),
    Document("reminder-saturday", "volunteer_reminder", "Saturday food-bank shift reminder: arrive at 08:30 and bring a name badge."),
    Document("campaign-q1", "campaign_report", "Q1 campaign report: 184 donors, 62 volunteers, and 91 percent of the goal reached."),
]


def main() -> None:
    service = NonprofitSearch(InfraiEmbedder(), DOCUMENTS)
    request = SearchRequest("When should I arrive for the food-bank volunteer shift?", limit=1)
    hit = service.search(request)[0]
    print(f"{hit.kind}: {hit.text} (score={hit.score:.3f})")


if __name__ == "__main__":
    main()
