# Entry point for running the project.

try:
    # Support running the file directly with: python src/main.py
    from ranker import annotate_ranked_listings, filter_listings
    from scraper import search_listings
except ImportError:
    # Support running as a module with: python -m src.main
    from src.ranker import annotate_ranked_listings, filter_listings
    from src.scraper import search_listings


def main() -> None:
    # Ask the user what they want to search for.
    keyword = input("Enter a search keyword: ").strip()

    # Stop early if the user did not enter anything useful.
    if not keyword:
        print("Keyword cannot be empty.")
        return

    # Fetch the raw listings for the entered keyword.
    listings = search_listings(keyword)

    # Remove obvious low-quality matches before ranking the remaining results.
    filtered_listings = filter_listings(listings, keyword)
    annotated_listings = annotate_ranked_listings(filtered_listings, keyword)

    # Print a simple heading before showing the results.
    print(f"\nFound {len(filtered_listings)} filtered listings for '{keyword}':\n")

    # Show each listing in a readable format.
    for index, item in enumerate(annotated_listings, start=1):
        listing = item["listing"]
        print(f"{index}. {listing.title}")
        print(f"   Score: {item['score']}")
        print(f"   Category: {item['category'] or 'unknown'}")
        print(f"   Detected model: {item['detected_model'] or 'unknown'}")
        print(f"   Target model: {item['target_model'] or 'unknown'}")
        print(f"   Model match: {'exact' if item['model_match'] else 'no'}")
        print(f"   Price: ${listing.price:.2f}")
        if item["market_price"] is not None and item["delta_percent"] is not None:
            print(f"   Market price: ${item['market_price']:.2f}")
            print(f"   Delta: {item['delta_percent']:+.1f}%")
            print(f"   Deal: {item['deal_label']}")
        elif item["market_price"] is not None:
            print(f"   Market price: ${item['market_price']:.2f}")
            print("   Delta: not comparable")
            print(f"   Deal: {item['deal_label'] or 'not_comparable'}")
        else:
            print("   Market price: unknown")
            print("   Delta: unknown")
            print(f"   Deal: {item['deal_label'] or 'unknown'}")
        print(f"   Source: {listing.source}")
        print(f"   URL: {listing.url}")

        # Only print optional fields when they have values.
        if listing.posted_at:
            print(f"   Posted at: {listing.posted_at}")

        if listing.description:
            print(f"   Description: {listing.description}")

        print()


if __name__ == "__main__":
    # Run the CLI only when this file is executed directly.
    main()
