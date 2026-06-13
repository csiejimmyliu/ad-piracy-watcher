# Implementation Brief — ad-piracy-watcher MVP

## What You Are Building
Implement the MVP for ad-piracy-watcher.
The repo contains a CLAUDE.md with the full spec — follow it exactly.

## Background (one sentence)
This tool visits known malicious websites and checks whether legitimate brand ads
appear on them, outputting (site, ad_domain, brand) pairs as evidence.

## What This MVP Validates
One question: do blacklisted sites actually serve legitimate brand ads?
If results.json has at least one pair after a run, the idea is validated.

## Hard Constraints
- Everything in the OUT list in CLAUDE.md must not be implemented — no exceptions
- Do not add features beyond what is specified, even "small improvements"
- ad_domains.json must be seeded with at least 30 real ad domains before running
- No LLM calls anywhere in this codebase

## Module Responsibilities

### urlhaus.py
- Call `https://urlhaus-api.abuse.ch/v1/urls/recent/`
- Filter for `url_status: "online"` only
- Return `List[str]` of URLs, capped at `MAX_SITES_PER_RUN`

### ad_detector.py
- Load ad_domains.json once at startup
- For each intercepted request URL: extract the domain, check against the lookup table
- Return `List[AdMatch]` — one entry per matched ad domain

### runner.py
- Use Playwright async, headless Chromium
- For each site URL:
  - Intercept all network requests via `page.on("request", ...)`
  - Wait for `networkidle` or `CRAWL_TIMEOUT` seconds, whichever comes first
  - Pass all intercepted request URLs to ad_detector
  - On timeout or exception: skip the site, continue
- Return all AdMatch results across all sites

### writer.py
- Load existing results.json if it exists
- Append new AdMatch entries
- Deduplicate by `(site_url + ad_domain)` — never write duplicate pairs
- Write back to results.json

### run_crawl.py
- Read env vars (MAX_SITES_PER_RUN, CRAWL_TIMEOUT)
- Call urlhaus.py → get site list
- Call runner.py → get AdMatch list
- Call writer.py → persist results
- Print summary: sites crawled, pairs found

## Acceptance Criteria
1. `python scripts/run_crawl.py` runs without errors
2. results.json is created and contains valid AdMatch records
3. Code is readable with no unnecessary abstractions
4. All 6 files from the implementation order exist

## Environment
- macOS
- Python 3.11+
- Install dependencies: `pip install playwright python-dotenv` then `playwright install chromium`
