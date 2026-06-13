import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

_AD_DOMAINS_PATH = Path(__file__).parent / "ad_domains.json"

with open(_AD_DOMAINS_PATH) as _f:
    _AD_DOMAINS: dict = json.load(_f)


@dataclass
class AdMatch:
    site_url: str
    site_domain: str
    ad_domain: str
    ad_brand: str
    ad_network: str
    ad_request_url: str
    crawled_at: str  # ISO 8601


def detect(site_url: str, request_url: str) -> AdMatch | None:
    try:
        request_host = urlparse(request_url).netloc.lower()
    except Exception:
        return None

    for ad_domain, meta in _AD_DOMAINS.items():
        if request_host == ad_domain or request_host.endswith("." + ad_domain):
            return AdMatch(
                site_url=site_url,
                site_domain=urlparse(site_url).netloc,
                ad_domain=ad_domain,
                ad_brand=meta["brand"],
                ad_network=meta["network"],
                ad_request_url=request_url,
                crawled_at=datetime.now(timezone.utc).isoformat(),
            )
    return None
