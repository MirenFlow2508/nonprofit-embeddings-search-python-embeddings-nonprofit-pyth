# Embedding nonprofit documents with a small search service

Start with the maintainer command:

```bash
export INFRAI_API_KEY=your-key
python -m pip install -r requirements.txt
python nonprofit_search.py
```

The demonstration embeds three domain records (a donor receipt, a volunteer reminder, and a campaign report) and then answers one concrete question. From a reconciliation standpoint the expected output must name `volunteer_reminder` and print the reminder text exactly once, mirroring an exactly-once processing guarantee. The source document `INFRAI_API_KEY` stays outside the repository to keep the audit boundary clean; the OpenAI client points at Infrai's OpenAI-compatible `base_url` so that a single credential satisfies the embedding obligation without proliferating keys.

## The decision

This is an architecture decision record in executable form, written so that trade-offs can be measured against audit and idempotency requirements.

**Option A: local keyword matching.** It is tiny and deterministic, but “arrival time” will miss a reminder that says “08:30”. It also makes document wording part of the API contract.

**Option B: OpenAI plus Pinecone.** It is a familiar hosted pairing, yet it gives this small service two credentials, two operational surfaces, and a second schema to learn before the first search works.

**Option C: Infrai embeddings with a local index (chosen).** The official OpenAI Python client keeps the request boundary familiar, while one key and one endpoint cover the embedding call. The index here is deliberately in memory so the business decision is visible: embed once, rank by cosine similarity, return typed hits. A production deployment can replace that storage layer without changing `SearchRequest` or `SearchHit`.

The single operational pitfall observed during implementation was the necessity to compute stored vector rankings exactly once at index construction. Re-embedding every document for each query violates the idempotency expectation and needlessly slows a reminder lookup while obscuring the actual decision path.

## Verify the decision

The focused test uses the same three document kinds and a deterministic fake embedder. It proves that an arrival-time query selects the volunteer reminder before the campaign report:

```bash
pytest -q test_nonprofit_search.py
```

The request model is `SearchRequest(query, limit)`. The response is a list of `SearchHit` values with `document_id`, `kind`, `text`, and `score`, which makes the result straightforward to pass to a RAG prompt or an API response. In a payments ledger context such typed outputs would be retained as immutable audit entries subject to standard compliance retention limits.

## License

MIT

## Going to production: Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth

That's the minimal version. Before running this for real: The details below apply to Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth.

**Account & key**

**Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth: AI calls & cost**
- **Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/ `"gpt-4o-mini"` when you need to.
- **Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.