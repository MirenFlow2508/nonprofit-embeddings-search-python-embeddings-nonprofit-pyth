from nonprofit_search import Document, NonprofitSearch, SearchRequest


class FakeEmbedder:
    vectors = {
        "receipt": [1.0, 0.0, 0.0],
        "volunteer": [0.0, 1.0, 0.0],
        "campaign": [0.0, 0.0, 1.0],
        "arrival": [0.0, 0.9, 0.1],
    }

    def embed(self, text: str):
        return self.vectors[text]


def test_volunteer_query_prioritizes_reminder():
    service = NonprofitSearch(
        FakeEmbedder(),
        [
            Document("r1", "donor_receipt", "receipt"),
            Document("v1", "volunteer_reminder", "volunteer"),
            Document("c1", "campaign_report", "campaign"),
        ],
    )

    result = service.search(SearchRequest("arrival", limit=2))

    assert [hit.document_id for hit in result] == ["v1", "c1"]
    assert result[0].score > result[1].score
