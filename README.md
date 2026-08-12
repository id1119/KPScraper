# KP Market Scanner

A lightweight Python tool for scraping and ranking listings from KupujemProdajem, focused on identifying relevant hardware offers and comparing them more intelligently.

## What it does

- Searches KupujemProdajem for a user-provided keyword
- Parses listing titles, prices and URLs
- Filters accessories, full-PC listings and mismatched categories
- Detects GPU models such as RTX, GTX and RX variants
- Scores and ranks listings by relevance
- Annotates results with model/category information and deal signals

## Tech stack

- Python
- Requests
- Beautiful Soup
- Regular expressions and rule-based ranking

## Project structure

```text
src/
  main.py       # CLI entry point
  scraper.py    # Fetching and HTML parsing
  ranker.py     # Filtering, model detection and ranking
  models.py     # Listing data model
data/
  sample.html   # Small parsing fixture
requirements.txt
```

## Running the project

Create a Python virtual environment, install the packages from `requirements.txt`, then run `python -m src.main` from the project root.

Enter a search term such as `RTX 3070`. The CLI prints filtered listings with ranking metadata, detected model information, price data and the source URL.

## Notes

This project is intended for learning and experimentation with web scraping, data filtering and ranking. Website structure can change over time, so scraping logic may require maintenance.

## Status

Prototype / active experiment.
