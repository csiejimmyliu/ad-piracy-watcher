import dataclasses
import json
from pathlib import Path

RESULTS_PATH = Path("results.json")


def save(matches: list) -> int:
    existing: list[dict] = []
    if RESULTS_PATH.exists():
        with open(RESULTS_PATH) as f:
            existing = json.load(f)

    seen = {(r["site_url"], r["ad_domain"]) for r in existing}
    new_entries = []
    for m in matches:
        key = (m.site_url, m.ad_domain)
        if key not in seen:
            seen.add(key)
            new_entries.append(dataclasses.asdict(m))

    with open(RESULTS_PATH, "w") as f:
        json.dump(existing + new_entries, f, indent=2)

    return len(new_entries)
