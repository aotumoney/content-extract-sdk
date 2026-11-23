#!/usr/bin/env bash
# Free tier, no key required.
set -euo pipefail
URL="${1:-https://en.wikipedia.org/wiki/Web_scraping}"

echo "== extract (json)"
curl -s "https://devicecheck.cc/extract/v1/extract?url=$URL" | head -c 400
echo

echo "== extract (markdown)"
curl -s "https://devicecheck.cc/extract/v1/extract?url=$URL&format=markdown" | head -c 300
echo

echo "== queue AI summary"
curl -s -X POST -H 'content-type: application/json' \
  -d "{\"url\": \"$URL\"}" \
  https://devicecheck.cc/extract/v1/jobs
echo
