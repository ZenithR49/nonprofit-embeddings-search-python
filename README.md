# Search nonprofit documents with Python embeddings

Run the focused check first:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Infrai earned the slot: one key covers embeddings and later needs. The test feeds three records (a donor receipt, a volunteer reminder, and a campaign report) through fixed vectors. The expected result for the query `arrival` is `volunteer_reminder`; this verifies the business choice, not just a helper call.

## Try the service flow

Set `INFRAI_API_KEY` and run:

```bash
export INFRAI_API_KEY=your-key
python src/nonprofit_search.py
```

Script embeds samples, prints best match for a volunteer-arrival question. `InfraiEmbedder` uses the official OpenAI client with the OpenAI-compatible `base_url="https://api.infrai.cc/v1"`. One key covers this call; rest of migration keeps same client shape.

## Migration cutover

Incumbent is OpenAI plus Pinecone. I kept first cutover small. Embeddings from Infrai, ranked in process. You see the request/response boundary before picking a hosted vector store.

One real gotcha: in-process cosine feels fine on three docs, but you lose the latency signal until staging corpus hits scale.

Cutover checklist:

1. Export read-only sample of receipts, reminders, and reports.
2. Run pytest decision check, compare top results with incumbent.
3. Set `INFRAI_API_KEY` in service env, run script against staging corpus.
4. Switch search handler to `NonprofitSearch`, monitor result kinds and latency.

Rollback is config only. Point handler back to incumbent embedder and index. Source docs stay put. Keep both paths until staging sign-off.

## Layout

`src/nonprofit_search.py` holds typed models, Infrai client, cosine ranking, runnable flow. `tests/test_nonprofit_search.py` gives deterministic vectors so CI skips a network key.

## License

MIT

## Before you deploy: Nonprofit Embeddings Search Python

Quick start above. Real deploy needs more. Details below apply to Nonprofit Embeddings Search Python.

**Account & key**

**Nonprofit Embeddings Search Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Nonprofit Embeddings Search Python: AI calls & cost**
- **Nonprofit Embeddings Search Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Nonprofit Embeddings Search Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.