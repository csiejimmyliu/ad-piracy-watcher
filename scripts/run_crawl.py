import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from blacklist.urlhaus import fetch_urls
from crawler.runner import crawl
from storage.writer import save


def main():
    print("Fetching blacklist from URLhaus...")
    urls = fetch_urls()
    print(f"  {len(urls)} sites to crawl")

    print("Crawling sites...")
    matches = asyncio.run(crawl(urls))
    print(f"  {len(matches)} ad matches found")

    added = save(matches)
    print(f"  {added} new pairs written to results.json")


if __name__ == "__main__":
    main()
