# Scraper module for collecting source data.

from models import Listing


def search_listings(keyword: str) -> list[Listing]:
    # Return sample data for now so the rest of the project can be tested.
    return [
        Listing(
            title=f"{keyword.title()} Laptop - Good Condition",
            price=450.0,
            url="https://example.com/listing-1",
            source="SampleMarket",
            posted_at="2026-03-29",
            description="A sample listing used for testing the application.",
        ),
        Listing(
            title=f"Used {keyword.title()} Bundle",
            price=299.99,
            url="https://example.com/listing-2",
            source="SampleMarket",
            posted_at="2026-03-28",
            description="Another sample result with a realistic-looking title.",
        ),
        Listing(
            title=f"{keyword.title()} Accessories Pack",
            price=89.5,
            url="https://example.com/listing-3",
            source="SampleMarket",
            posted_at="2026-03-27",
            description="A lower-priced test listing for CLI output.",
        ),
    ]
