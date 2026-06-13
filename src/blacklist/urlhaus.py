import json
import os
import urllib.request

_URLHAUS_API = "https://urlhaus-api.abuse.ch/v1/urls/recent/"


def fetch_urls() -> list[str]:
    max_sites = int(os.getenv("MAX_SITES_PER_RUN", "50"))

    req = urllib.request.Request(_URLHAUS_API, method="POST", data=b"")
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    urls = [
        entry["url"]
        for entry in data.get("urls", [])
        if entry.get("url_status") == "online"
    ]
    return urls[:max_sites]
