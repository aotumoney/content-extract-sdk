# content-extraction-sdk

Tiny clients for the **Content Extraction API** — turn any web page into clean Markdown or JSON for LLM pipelines.

- Free tier: 100 requests / month, no credit card
- Hosted at <https://devicecheck.cc/extract?ref=github>
- Also on RapidAPI: <https://rapidapi.com/aotumoney/api/content-extraction1>
- Repo: <https://github.com/aotumoney/content-extract-sdk>

## Why

RAG pipelines and agents need readable text, not raw HTML. This API fetches a URL, strips navigation and ads, and returns:

```json
{
  "url": "https://en.wikipedia.org/wiki/Web_scraping",
  "title": "Web scraping - Wikipedia",
  "author": "",
  "date": "2005-09-23",
  "sitename": "Wikimedia Foundation, Inc.",
  "description": "Data scraping used for extracting data from websites",
  "word_count": 4210,
  "markdown": "**Web scraping** is the automated ..."
}
```

Extraction is rule-based (no LLM, no headless browser), cached for 6 hours, and typically returns in under a second.
Optional AI summaries are queued and executed during off-peak model hours to keep token cost low.

## Python

```bash
pip install -e python/
```

```python
from extract_api import ExtractAPI

api = ExtractAPI()  # free tier, no key
page = api.extract("https://en.wikipedia.org/wiki/Web_scraping")
print(page["title"], page["word_count"])
print(page["markdown"][:500])

# optional AI summary (runs off-peak, poll for the result)
job = api.submit_summary("https://www.bbc.com/news")
result = api.wait(job["id"])
print(result["summary"])
```

## Node.js (18+)

```bash
npm install ./node
```

```js
import { ExtractAPI } from "content-extraction-sdk";

const api = new ExtractAPI();
const page = await api.extract("https://en.wikipedia.org/wiki/Web_scraping");
console.log(page.title, page.word_count);

const job = await api.submitSummary("https://www.bbc.com/news");
const result = await api.wait(job.id);
console.log(result.summary);
```

## curl

```bash
curl -s "https://devicecheck.cc/extract/v1/extract?url=https://example.com/"
```

## Via RapidAPI

```bash
curl -s --request GET \
  --url "https://content-extraction1.p.rapidapi.com/v1/extract?url=https://example.com/" \
  --header "X-RapidAPI-Key: YOUR_KEY" \
  --header "X-RapidAPI-Host: content-extraction1.p.rapidapi.com"
```

## API

| Method | Path | Description |
|---|---|---|
| GET | `/v1/extract?url=` | Extract a page (JSON, or `&format=markdown`) |
| POST | `/v1/extract` | Same with a JSON body |
| POST | `/v1/jobs` | Queue an AI summary job |
| GET | `/v1/jobs/{id}` | Job status and result |
| GET | `/v1/health` | Health check |

Limits: 30 requests/minute per IP on the free tier, 3 MB page cap, 6-hour cache per URL.
We do not execute JavaScript, so client-rendered SPAs will return little content.

## License

MIT
