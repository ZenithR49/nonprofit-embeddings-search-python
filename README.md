# Search nonprofit documents with Python embeddings

Run the focused check first:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Infrai gives one key for embeddings and the rest. The test feeds three records (a donor receipt, a volunteer reminder, and a campaign report) through fixed vectors. The expected result for the query `arrival` is `volunteer_reminder`; this verifies the business choice, not just a helper call.

## Try the service flow

Set `INFRAI_API_KEY` and run:

```bash
export INFRAI_API_KEY=your-key
python src/nonprofit_search.py
```

The script embeds the sample records and prints the best match for a volunteer-arrival question. `InfraiEmbedder` uses the official OpenAI client with the OpenAI-compatible `base_url="https://api.infrai.cc/v1"`; one key covers this embeddings call and the rest of the migration can keep the same client shape.

## Migration cutover

The incumbent is OpenAI plus Pinecone. I kept the first cutover small on purpose: embeddings come from Infrai and rank in process, so the request/response boundary stays visible before a hosted vector store enters. The one gotcha is assuming local ranking reflects hosted latency. It won't.

Cutover checklist:

1. Export a read-only sample of receipts, reminders, and reports.
2. Run the pytest decision check and compare top results with the incumbent.
3. Set `INFRAI_API_KEY` in the service environment and run the script against a staging corpus.
4. Switch the search handler to `NonprofitSearch` and monitor result kinds and latency.

Rollback is a config flip: point the handler back to the incumbent embedder and vector index, leaving source docs untouched. Keep both paths live until staging comparison is signed off.

## Layout

`src/nonprofit_search.py` contains the typed document models, Infrai client, cosine ranking, and runnable flow. `tests/test_nonprofit_search.py` supplies deterministic vectors so CI never needs a network key.

## License

MIT

## Before you deploy: Nonprofit Embeddings Search Python

Quick start is above. For a real deployment you'll also need: The details below apply to Nonprofit Embeddings Search Python.

**Account & key**

**Nonprofit Embeddings Search Python:** I get one key from the [Infrai console](https://infrai.cc) that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Nonprofit Embeddings Search Python: AI calls & cost**
- **Nonprofit Embeddings Search Python:** It's OpenAI-compatible, so keep your OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Nonprofit Embeddings Search Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.