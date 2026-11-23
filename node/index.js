const DEFAULT_BASE = "https://devicecheck.cc/extract"; // docs: https://devicecheck.cc/extract?ref=github

export class ExtractAPI {
  constructor({ base = DEFAULT_BASE, apiKey = null, rapidapiKey = null, timeoutMs = 60000 } = {}) {
    this.base = base.replace(/\/$/, "");
    this.apiKey = apiKey;
    this.rapidapiKey = rapidapiKey;
    this.timeoutMs = timeoutMs;
  }

  _headers() {
    const h = { Accept: "application/json" };
    if (this.apiKey) h["X-API-Key"] = this.apiKey;
    if (this.rapidapiKey) {
      h["X-RapidAPI-Key"] = this.rapidapiKey;
      h["X-RapidAPI-Host"] = "content-extraction1.p.rapidapi.com";
    }
    return h;
  }

  async _request(method, path, { params, body } = {}) {
    let url = this.base + path;
    if (params) url += "?" + new URLSearchParams(params).toString();
    const init = { method, headers: this._headers(), signal: AbortSignal.timeout(this.timeoutMs) };
    if (body !== undefined) {
      init.headers["Content-Type"] = "application/json";
      init.body = JSON.stringify(body);
    }
    const res = await fetch(url, init);
    const text = await res.text();
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${text.slice(0, 300)}`);
    return JSON.parse(text);
  }

  /** Page dict: title, markdown, word_count, ... */
  extract(url, format = "json") {
    return this._request("GET", "/v1/extract", { params: { url, format } });
  }

  /** Just the Markdown string. */
  async extractMarkdown(url) {
    const res = await fetch(`${this.base}/v1/extract?` + new URLSearchParams({ url, format: "markdown" }),
      { headers: this._headers(), signal: AbortSignal.timeout(this.timeoutMs) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.text();
  }

  /** Queue an AI summary (runs off-peak). */
  async submitSummary(url) {
    const data = await this._request("POST", "/v1/jobs", { body: { url, task: "summary" } });
    return data.job;
  }

  async getJob(id) {
    return (await this._request("GET", `/v1/jobs/${id}`)).job;
  }

  /** Poll until done. */
  async wait(id, { timeoutMs = 900000, intervalMs = 15000 } = {}) {
    const start = Date.now();
    while (Date.now() - start < timeoutMs) {
      const job = await this.getJob(id);
      if (job.status === "done") return job.result;
      if (job.status === "error") throw new Error(job.error || "job failed");
      await new Promise((r) => setTimeout(r, intervalMs));
    }
    throw new Error(`job ${id} timed out`);
  }
}
