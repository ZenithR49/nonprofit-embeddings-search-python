from src.nonprofit_search import Document, NonprofitSearch


class FixedEmbedder:
    vectors = {
        "receipt": [1.0, 0.0],
        "shift": [0.0, 1.0],
        "campaign": [0.7, 0.7],
        "arrival": [0.0, 1.0],
    }

    def embed(self, text: str):
        return self.vectors[text]


def test_volunteer_query_ranks_shift_reminder_first():
    search = NonprofitSearch(FixedEmbedder())
    search.add(Document("donor_receipt", "receipt"))
    search.add(Document("volunteer_reminder", "shift"))
    search.add(Document("campaign_report", "campaign"))

    result = search.search("arrival", limit=1)[0]

    assert result.document.kind == "volunteer_reminder"
    assert result.score == 1.0
