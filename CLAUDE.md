# CLAUDE.md — ad-piracy-watcher

## Purpose
A crawler tool that visits known blacklisted websites, intercepts ad requests,
and outputs (site, ad_domain, brand) pairs to verify whether legitimate brand ads
appear on malicious websites.

## MVP Scope

**IN:**
- Single blacklist source: URLhaus (abuse.ch)
- Async Playwright headless crawler that intercepts all network requests
- Static ad_domains.json to match ad domains → brand
- Output results.json, run locally

**OUT (explicitly excluded — do not implement):**
- Screenshots or HAR files
- proof/ or any proof mechanism
- PhishTank, Google Transparency, or other blacklist sources
- GitHub Actions CI/CD
- Separate database repo
- index.json

## Tech Stack
- Python 3.11+
- Playwright (async)
- No LLM dependency

## Project Structure
```
ad-piracy-watcher/
├── CLAUDE.md
├── pyproject.toml
├── src/
│   ├── blacklist/
│   │   └── urlhaus.py       # Fetch URLhaus blacklist, return List[str] (urls)
│   ├── crawler/
│   │   ├── runner.py        # Playwright visitor + request interception
│   │   ├── ad_detector.py   # Match against ad_domains.json, return List[AdMatch]
│   │   └── ad_domains.json  # domain → {brand, network}
│   └── storage/
│       └── writer.py        # Append to results.json, deduplicate by (site_url + ad_domain)
└── scripts/
    └── run_crawl.py         # Entry point — wires all modules together
```

## Data Formats

### AdMatch (dataclass)
```python
@dataclass
class AdMatch:
    site_url: str
    site_domain: str
    ad_domain: str
    ad_brand: str
    ad_network: str
    ad_request_url: str
    crawled_at: str   # ISO 8601
```

### results.json
```json
[
  {
    "site_url": "http://example-malware.com",
    "site_domain": "example-malware.com",
    "ad_domain": "googlesyndication.com",
    "ad_brand": "Google",
    "ad_network": "Google Ads",
    "ad_request_url": "https://googlesyndication.com/...",
    "crawled_at": "2026-06-12T00:00:00Z"
  }
]
```

### ad_domains.json (seed — at least 30 entries)
```json
{
  "googlesyndication.com":  {"brand": "Google",  "network": "Google Ads"},
  "doubleclick.net":        {"brand": "Google",  "network": "Google Ads"},
  "amazon-adsystem.com":    {"brand": "Amazon",  "network": "Amazon DSP"},
  "ads.twitter.com":        {"brand": "X",       "network": "X Ads"},
  "facebook.com/tr":        {"brand": "Meta",    "network": "Meta Audience Network"}
}
```

## Environment Variables
```
MAX_SITES_PER_RUN=50    # MVP: crawl 50 sites per run
CRAWL_TIMEOUT=15        # Per-site timeout in seconds
```

## How to Run
```bash
python scripts/run_crawl.py
# outputs results.json
```

## Success Criteria
results.json contains at least 1 pair after a run → idea validated.

## Implementation Order
1. `ad_domains.json` — populate with 30 common ad domains
2. `ad_detector.py` — match request URL domains against the lookup table
3. `urlhaus.py` — call URLhaus API, return list of site URLs
4. `runner.py` — Playwright async, intercept requests, pass to detector
5. `writer.py` — append to results.json, deduplicate by (site_url + ad_domain)
6. `run_crawl.py` — wire everything together, run locally
