# Data models used by the project.

from dataclasses import dataclass
from typing import Optional


@dataclass
class Listing:
    # Represents one listing returned by the scraper.
    title: str
    price: float
    url: str
    source: str
    posted_at: Optional[str] = None
    description: Optional[str] = None
