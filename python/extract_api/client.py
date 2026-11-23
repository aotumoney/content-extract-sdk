"""Minimal Python client for the Content Extraction API."""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = "https://devicecheck.cc/extract"


class ExtractAPI:
    def __init__(self, base=DEFAULT_BASE, api_key=None, rapidapi_key=None, timeout=60):
        self.base = base.rstrip("/")
        self.api_key = api_key
        self.rapidapi_key = rapidapi_key
        self.timeout = timeout

    def _headers(self):
        h = {"Accept": "application/json"}
        if self.api_key:
            h["X-API-Key"] = self.api_key
        if self.rapidapi_key:
            h["X-RapidAPI-Key"] = self.rapidapi_key
            h["X-RapidAPI-Host"] = "content-extraction1.p.rapidapi.com"
        return h

    def _request(self, method, path, params=None, body=None):
        url = self.base + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers=self._headers())
        if data:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise RuntimeError("HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:300]))

    def extract(self, url, fmt="json"):
        """Return the parsed page dict (title, markdown, word_count, ...)."""
        return self._request("GET", "/v1/extract", params={"url": url, "format": fmt})

    def extract_markdown(self, url):
        """Return just the Markdown string."""
        q = urllib.parse.urlencode({"url": url, "format": "markdown"})
        req = urllib.request.Request(self.base + "/v1/extract?" + q, headers=self._headers())
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.read().decode("utf-8", "replace")

    def submit_summary(self, url):
        """Queue an AI summary job (executed during off-peak model hours)."""
        return self._request("POST", "/v1/jobs", body={"url": url, "task": "summary"})["job"]

    def get_job(self, job_id):
        return self._request("GET", "/v1/jobs/" + job_id)["job"]

    def wait(self, job_id, timeout=900, interval=15):
        """Block until the job finishes. Raises on error or timeout."""
        waited = 0
        while waited < timeout:
            job = self.get_job(job_id)
            if job["status"] == "done":
                return job["result"]
            if job["status"] == "error":
                raise RuntimeError(job.get("error") or "job failed")
            time.sleep(interval)
            waited += interval
        raise TimeoutError("job %s still %s after %ss" % (job_id, job["status"], timeout))
