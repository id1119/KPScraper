# KP Market Scanner

A lightweight Python tool for scraping and ranking listings from KupujemProdajem, with filtering logic focused on identifying relevant hardware offers and comparing them more intelligently.

## What it does

- Searches KupujemProdajem for a user-provided keyword
- Parses listing titles, prices and URLs
- Filters obvious accessories, full-PC listings and mismatched categories
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
  config.py     # Configuration
  ai_eval.py    # Evaluation-related helpers
data/            # Local/debug data
requirements.txt
```

## Getting started

```bash
git clone https://github.com/id1119/KPScraper.git
cd KPScraper
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

Then enter a search term, for example:

```text
RTX 3070
```

The CLI prints filtered listings together with ranking metadata, detected model information, price data and the source URL.

## Notes

This project is intended for learning and experimentation with web scraping, data filtering and ranking. Website structure can change over time, so scraping logic may require maintenance.

## Status

Prototype / active experiment.
