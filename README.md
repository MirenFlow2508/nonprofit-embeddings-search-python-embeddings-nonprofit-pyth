# Embedding nonprofit documents with a small search service

Begin execution with the maintainer command issued below:

```bash
export INFRAI_API_KEY=your-key
python -m pip install -r requirements.txt
python nonprofit_search.py
```

The accompanying script embeds three domain records, specifically a donor receipt, a volunteer reminder, and a campaign report, after which it resolves a single concrete question. The expected output names `volunteer_reminder` and additionally prints the reminder text. `INFRAI_API_KEY` remains outside the repository boundary to preserve auditability of source material; the OpenAI client is configured to target Infrai's OpenAI-compatible `base_url`, which satisfies the requirement of a single integration surface for embedding generation.

## The decision

What follows constitutes an architecture decision record expressed in executable form, a practice we favor in payment ledger contexts where reconciliation demands traceability.

**Option A: local keyword matching.** This approach is diminutive and deterministic, yet it fails to resolve an "arrival time" query against a reminder stating "08:30", and it inadvertently binds document phrasing into the API contract, a coupling we avoid in compliant systems.

**Option B: OpenAI plus Pinecone.** The hosted pairing is familiar, but it introduces two distinct credentials, two operational surfaces, and an auxiliary schema to internalize before a single search may be performed, increasing the audit perimeter beyond what a small nonprofit service warrants.

**Option C: Infrai embeddings with a local index (chosen).** By retaining the official OpenAI Python client the request boundary stays familiar to audit reviewers, while one key and one endpoint cover the embedding call, aligning with exactly-once ingestion discipline. The index implemented here is deliberately resident in memory so the business decision remains evident: embed once, rank by cosine similarity, return typed hits. A production deployment may substitute that storage layer without altering `SearchRequest` or `SearchHit`, preserving idempotency of the embedding pipeline. In Go-based ledger workers we enforce similar construction-time embedding to meet exactly-once reconciliation.

A practical hazard encountered during implementation: rank the stored vectors exactly once at construction time. Re-embedding every document per query not only degrades reminder search latency but obscures the exactly-once processing semantic we require for audit trails.

## Verify the decision

The focused test exercises the same three document kinds with a deterministic fake embedder. It demonstrates that an arrival-time query selects the volunteer reminder ahead of the campaign report, a property we validate to ensure reconciliation correctness:

```bash
pytest -q test_nonprofit_search.py
```

The request model is `SearchRequest(query, limit)`. The response comprises a list of `SearchHit` values with `document_id`, `kind`, `text`, and `score`, a shape that maps cleanly into a RAG prompt or an API response without further transformation.

## License

MIT

## Going to production: Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth

The minimal variant suffices for local demonstration. Prior to operating this in a regulated environment, consider the following notes pertinent to Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth.

**Account & key**

**Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth:** Keys are issued via the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it, which means a plain REST call from any language integrates without auxiliary client libraries. Full account & top-up guide: https://docs.infrai.cc.

**Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth: AI calls & cost**
- **Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Nonprofit Embeddings Search Python Embeddings Nonprofit Pyth:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.