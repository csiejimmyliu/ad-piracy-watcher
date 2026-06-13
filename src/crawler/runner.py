import os

from playwright.async_api import Browser, async_playwright

from .ad_detector import AdMatch, detect


async def crawl(site_urls: list[str]) -> list[AdMatch]:
    timeout_ms = int(os.getenv("CRAWL_TIMEOUT", "15")) * 1000
    results: list[AdMatch] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for site_url in site_urls:
            matches = await _visit(browser, site_url, timeout_ms)
            results.extend(matches)
        await browser.close()

    return results


async def _visit(browser: Browser, site_url: str, timeout_ms: int) -> list[AdMatch]:
    intercepted: list[str] = []
    page = None

    try:
        page = await browser.new_page()
        page.on("request", lambda req: intercepted.append(req.url))
        await page.goto(site_url, timeout=timeout_ms, wait_until="networkidle")
    except Exception:
        pass
    finally:
        if page:
            try:
                await page.close()
            except Exception:
                pass

    matches = []
    for req_url in intercepted:
        match = detect(site_url, req_url)
        if match:
            matches.append(match)
    return matches
