# Scraper module for collecting source data.

import re
from pathlib import Path
from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup
import requests

try:
    # Support running as a simple script from inside the src folder.
    from models import Listing
except ImportError:
    # Support importing the module from the project root as src.scraper.
    from src.models import Listing

BASE_SITE_URL = "https://www.kupujemprodajem.com"


def build_search_url(keyword: str) -> str:
    # Build the search page URL and let urlencode handle spaces safely.
    query_string = urlencode({"keywords": keyword})
    return f"{BASE_SITE_URL}/pretraga?{query_string}"


def fetch_html(url: str) -> str:
    # Fetch one search results page and return its HTML.
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/136.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        # Return an empty string if the request fails for any reason.
        return ""

    return response.text


def save_debug_html(html: str) -> None:
    # Save the last fetched response so the parser can be debugged locally.
    if not html:
        return

    debug_path = Path(__file__).resolve().parent.parent / "data" / "last_response.html"
    debug_path.write_text(html, encoding="utf-8")


def parse_listings(html: str, keyword: str) -> list[Listing]:
    # Parse the fetched HTML and collect listing blocks that match the keyword.
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    listings: list[Listing] = []
    keyword_lower = keyword.lower()
    seen_urls: set[str] = set()

    # Try to pull listings from link elements on the search results page.
    for link_tag in soup.find_all("a", href=True):
        try:
            title = link_tag.get_text(" ", strip=True)
            href = link_tag.get("href", "").strip()

            # Skip empty titles and non-matching search results.
            if not title or keyword_lower not in title.lower():
                continue

            # Skip unusable links.
            if not href or href.startswith("#") or href.startswith("javascript:"):
                continue

            full_url = urljoin(BASE_SITE_URL, href)
            if full_url in seen_urls:
                continue

            # Look around the link for a nearby price on the same result block.
            container = link_tag.find_parent(["article", "div", "li"]) or link_tag.parent
            if container is None:
                continue

            container_text = container.get_text(" ", strip=True)
            price_match = re.search(r"(\d[\d\s\.,]*)\s*(€|eur|din)", container_text, re.IGNORECASE)
            if price_match is None:
                continue

            price_text = price_match.group(1).replace(" ", "")

            # Convert the matched price to a float and skip invalid values.
            if "," in price_text:
                normalized_price = price_text.replace(".", "").replace(",", ".")
            elif price_text.count(".") > 1:
                normalized_price = price_text.replace(".", "")
            else:
                normalized_price = price_text

            price = float(normalized_price)
        except (TypeError, ValueError):
            # Skip any listing that does not fit the expected simple format.
            continue

        listings.append(
            Listing(
                title=title,
                price=price,
                url=full_url,
                source="KupujemProdajem",
            )
        )
        seen_urls.add(full_url)

    return listings


def search_listings(keyword: str) -> list[Listing]:
    # Build the search URL, fetch the page, save it for debugging, then parse it.
    url = build_search_url(keyword)
    html = fetch_html(url)
    save_debug_html(html)
    return parse_listings(html, keyword)
