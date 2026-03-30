# Entry point for running the project.

try:
    # Support running the file directly with: python src/main.py
    from scraper import search_listings
except ImportError:
    # Support running as a module with: python -m src.main
    from src.scraper import search_listings


def main() -> None:
    # Ask the user what they want to search for.
    keyword = input("Enter a search keyword: ").strip()

    # Stop early if the user did not enter anything useful.
    if not keyword:
        print("Keyword cannot be empty.")
        return

    # Fetch the sample listings for the entered keyword.
    listings = search_listings(keyword)

    # Print a simple heading before showing the results.
    print(f"\nFound {len(listings)} listings for '{keyword}':\n")

    # Show each listing in a readable format.
    for index, listing in enumerate(listings, start=1):
        print(f"{index}. {listing.title}")
        print(f"   Price: ${listing.price:.2f}")
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
