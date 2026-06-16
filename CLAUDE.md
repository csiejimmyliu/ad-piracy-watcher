# CLAUDE.md — ad-piracy-watcher

## Purpose
A crawler tool that visits known piracy/copyright-infringing websites, intercepts ad requests,
and outputs (site, ad_domain, brand) pairs to verify whether legitimate brand ads appear on
piracy sites.

**Core hypothesis:** Major brands (e.g. Nintendo, Sony) inadvertently fund piracy sites by
having their ads served there via ad networks like Google Ads. This tool collects evidence.

**Why piracy sites specifically:** Piracy sites sustain themselves through ad revenue, so they
actively run ad networks. Malware distribution URLs and phishing sites are excluded — malware
URLs return binaries (no HTML, no ads), and phishing sites drive revenue through redirection,
not advertising.

## Roadmap

### Stage 1 — Validate the pipeline and hypothesis (current)
- **Blacklist source:** Manual list of domains from the USTR Notorious Markets List (hand-curated)
- **Goal 1 (technical):** `results.json` contains at least 1 pair → pipeline works end-to-end
- **Goal 2 (hypothesis):** At least 1 real brand ad found on a USTR-listed piracy site → idea validated
- **Fallback:** If USTR list yields no results, try another credible manual list before moving on

### Stage 2a — USTR PDF parser
- Automatically extract domains from the USTR Notorious Markets List PDF
- **Done when:** Extracted domain list matches the hand-curated Stage 1 list

### Stage 2b — Generic PDF parser
- Generalise Stage 2a to work on any similarly structured blacklist PDF report
- USTR is the first use case; the tool should handle others without code changes

### Stage 3 — Multiple blacklist sources
- Add additional credible blacklist sources (e.g. court-ordered blocking lists, other gov reports)
- Sources are independent — no ordering required between them
- Output still goes to a single `results.json`; per-source breakdown TBD when Stage 3 begins

## MVP Scope (Stage 1)

**IN:**
- Single blacklist source: hand-curated USTR Notorious Markets domain list (`src/blacklist/ustr.py`)
- Async Playwright headless crawler that intercepts all network requests
- Static `ad_domains.json` to match ad domains → brand
- Output `results.json`, run locally

**OUT (explicitly excluded from Stage 1 — do not implement):**
- Screenshots or HAR files
- proof/ or any proof mechanism
- PDF parsing (Stage 2)
- Multiple blacklist sources (Stage 3)
- PhishTank, Google Transparency, or other blacklist sources
  *(Reason: phishing sites drive revenue through redirection, not advertising — wrong target)*
- URLhaus or other malware-URL feeds
  *(Reason: URLhaus lists binary download endpoints, not HTML pages — no ads possible)*
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
│   │   └── ustr.py          # Return hand-curated USTR domain list as List[str]
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
    "site_url": "https://thepiratebay.org",
    "site_domain": "thepiratebay.org",
    "ad_domain": "googlesyndication.com",
    "ad_brand": "Google",
    "ad_network": "Google Ads",
    "ad_request_url": "https://pagead2.googlesyndication.com/...",
    "crawled_at": "2026-06-15T00:00:00Z"
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
  "connect.facebook.net":   {"brand": "Meta",    "network": "Meta Audience Network"}
}
```

## Environment Variables
```
MAX_SITES_PER_RUN=50    # Stage 1: crawl up to 50 sites per run
CRAWL_TIMEOUT=15        # Per-site timeout in seconds
```

## How to Run
```bash
uv run python scripts/run_crawl.py
# outputs results.json
```

## Blacklist Source: USTR Notorious Markets List
- Published annually by the US Trade Representative (credible, government source)
- Lists online markets known for copyright piracy and counterfeiting
- 2025 edition (released March 2026): ~37 online markets
- Notable inclusions: The Pirate Bay, 1337X, RuTracker, YTS.mx, Libgen, Sci-Hub, Anna's Archive
- Stage 1: domains hand-curated into `src/blacklist/ustr.py`
- Stage 2: automated PDF parser replaces the hand-curated list
- Source: https://ustr.gov/about/policy-offices/press-office/press-releases/2026/march/ustr-releases-2025-review-notorious-markets-counterfeiting-and-piracy
