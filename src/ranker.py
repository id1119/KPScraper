# Ranking module for ordering scraped results.

import re
from statistics import median
from urllib.parse import urlparse

try:
    # Support running the file directly from inside the src folder.
    from models import Listing
except ImportError:
    # Support importing the module from the project root as src.ranker.
    from src.models import Listing

_ACCESSORY_KEYWORDS = (
    "ventilator",
    "ventilatori",
    "fan",
    "kuler",
    "kuleri",
    "hladnjak",
    "adapter",
)

_FULL_PC_KEYWORDS = (
    "racunar",
    "racunari",
    "kompjuter",
    "kompjuteri",
    "pc",
    "konfiguracija",
)

_GPU_HINT_KEYWORDS = (
    "gpu",
    "graficka",
    "graphics card",
    "video card",
    "rtx",
    "gtx",
    "rx",
    "radeon",
    "geforce",
)

_GPU_VARIANT_KEYWORDS = ("ti", "super", "xt")
_WRONG_GPU_CATEGORIES = (
    "kompjuteri",
    "polovni-kompjuteri",
    "gejmerska-oprema",
    "kuleri",
)
_STRONG_FULL_PC_TERMS = (
    "ryzen",
    "intel",
    "i5",
    "i7",
    "ssd",
    "hdd",
    "ddr4",
    "ddr5",
    "gamer",
    "racunar",
    "kompjuter",
)


def normalize_text(text: str) -> str:
    # Lowercase the text and collapse repeated whitespace.
    return re.sub(r"\s+", " ", text.lower()).strip()


def _contains_word(text: str, word: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text) is not None


def _contains_any_word(text: str, words: tuple[str, ...]) -> bool:
    return any(_contains_word(text, word) for word in words)


def extract_gpu_model(text: str) -> str | None:
    normalized_text = normalize_text(text)
    patterns = (
        r"\b(rtx\s*\d{3,4}\s*(?:ti|super)?)\b",
        r"\b(gtx\s*\d{3,4}\s*(?:ti|super)?)\b",
        r"\b(rx\s*\d{4}\s*(?:xt)?)\b",
    )

    for pattern in patterns:
        match = re.search(pattern, normalized_text)
        if match is not None:
            return re.sub(r"\s+", " ", match.group(1)).strip()

    return None


def get_target_model(keyword: str) -> str | None:
    return extract_gpu_model(keyword)


def extract_category_from_url(url: str) -> str:
    parsed_url = urlparse(url)
    path_segments = [segment for segment in parsed_url.path.lower().split("/") if segment]

    preferred_categories = (
        "graficke-kartice",
        "polovni-kompjuteri",
        "kompjuteri",
        "gejmerska-oprema",
        "kuleri",
    )
    for category in preferred_categories:
        if category in path_segments:
            return category

    for segment in reversed(path_segments):
        if re.search(r"[a-z]", segment):
            return segment

    return ""


def _is_gpu_search(keyword: str) -> bool:
    normalized_keyword = normalize_text(keyword)
    return _contains_any_word(normalized_keyword, ("rtx", "gtx", "rx", "graficka"))


def is_wrong_category_for_gpu(url: str, keyword: str) -> bool:
    if not _is_gpu_search(keyword):
        return False

    category = extract_category_from_url(url)
    return category in _WRONG_GPU_CATEGORIES


def is_full_pc_title(title: str) -> bool:
    normalized_title = normalize_text(title)
    matched_terms = {
        term for term in _STRONG_FULL_PC_TERMS if _contains_word(normalized_title, term)
    }
    return len(matched_terms) >= 2


def _has_gpu_model(title: str) -> bool:
    return extract_gpu_model(title) is not None


def _has_gpu_hint(title: str) -> bool:
    normalized_title = normalize_text(title)
    return _has_gpu_model(normalized_title) or _contains_any_word(normalized_title, _GPU_HINT_KEYWORDS)


def classify_listing_title(title: str) -> str:
    normalized_title = normalize_text(title)

    if is_accessory_or_part(normalized_title):
        return "accessory_or_part"

    if is_full_pc(normalized_title):
        return "full_pc"

    if not _has_gpu_hint(normalized_title):
        return "unknown"

    extracted_model = extract_gpu_model(normalized_title)
    if extracted_model:
        if any(_contains_word(extracted_model, variant) for variant in _GPU_VARIANT_KEYWORDS):
            return "gpu_variant"
        return "exact_gpu"

    return "unknown"


def is_accessory_or_part(title: str) -> bool:
    normalized_title = normalize_text(title)
    return _contains_any_word(normalized_title, _ACCESSORY_KEYWORDS)


def is_full_pc(title: str) -> bool:
    normalized_title = normalize_text(title)
    return _contains_any_word(normalized_title, _FULL_PC_KEYWORDS) or is_full_pc_title(normalized_title)


def is_exact_model_match(title: str, keyword: str) -> bool:
    target_model = get_target_model(keyword)
    listing_model = extract_gpu_model(title)

    if target_model is None or listing_model is None:
        return False

    return listing_model == target_model


def is_model_variant_mismatch(title: str, keyword: str) -> bool:
    target_model = get_target_model(keyword)
    listing_model = extract_gpu_model(title)

    if target_model is None or listing_model is None:
        return False

    if listing_model == target_model:
        return False

    target_base = re.sub(r"\s+(ti|super|xt)\b", "", target_model).strip()
    listing_base = re.sub(r"\s+(ti|super|xt)\b", "", listing_model).strip()
    return target_base == listing_base


def is_variant_mismatch(title: str, keyword: str) -> bool:
    return is_model_variant_mismatch(title, keyword)


def is_suspicious_price(listing: Listing, keyword: str) -> bool:
    normalized_keyword = normalize_text(keyword)

    if "rtx 3070" in normalized_keyword and listing.price < 100:
        return True

    return False


def filter_listings(listings: list[Listing], keyword: str) -> list[Listing]:
    filtered_listings: list[Listing] = []

    for listing in listings:
        title = listing.title

        if is_accessory_or_part(title):
            continue

        if is_wrong_category_for_gpu(listing.url, keyword):
            continue

        if is_full_pc_title(title):
            continue

        if is_full_pc(title):
            continue

        if is_suspicious_price(listing, keyword):
            continue

        filtered_listings.append(listing)

    return filtered_listings


def score_listing(listing: Listing, keyword: str) -> int:
    normalized_title = normalize_text(listing.title)
    normalized_keyword = normalize_text(keyword)
    classification = classify_listing_title(normalized_title)
    category = extract_category_from_url(listing.url)

    score = 0

    if normalized_keyword in normalized_title:
        score += 80

    if classification == "exact_gpu":
        score += 40
    elif classification == "gpu_variant":
        score += 20
    elif classification == "unknown":
        score -= 10

    if _has_gpu_hint(normalized_title):
        score += 15

    if category == "graficke-kartice":
        score += 35

    if _is_gpu_search(normalized_keyword) and category and category != "graficke-kartice":
        score -= 40

    if is_variant_mismatch(normalized_title, normalized_keyword):
        score -= 50

    if is_accessory_or_part(normalized_title):
        score -= 80

    if is_wrong_category_for_gpu(listing.url, normalized_keyword):
        score -= 120

    if is_full_pc_title(normalized_title):
        score -= 120

    if is_full_pc(normalized_title):
        score -= 80

    if is_suspicious_price(listing, normalized_keyword):
        score -= 60

    return score


def rank_listings(listings: list[Listing], keyword: str) -> list[tuple[Listing, int]]:
    scored_listings = [(listing, score_listing(listing, keyword)) for listing in listings]
    return sorted(scored_listings, key=lambda item: item[1], reverse=True)


def estimate_market_price(listings: list[Listing], keyword: str) -> float | None:
    exact_model_prices: list[float] = []

    for listing in listings:
        category = extract_category_from_url(listing.url)

        if is_accessory_or_part(listing.title):
            continue

        if is_wrong_category_for_gpu(listing.url, keyword):
            continue

        if is_full_pc_title(listing.title) or is_full_pc(listing.title):
            continue

        if is_model_variant_mismatch(listing.title, keyword):
            continue

        if is_suspicious_price(listing, keyword):
            continue

        if category != "graficke-kartice":
            continue

        if not is_exact_model_match(listing.title, keyword):
            continue

        exact_model_prices.append(listing.price)

    if len(exact_model_prices) >= 3:
        return float(median(exact_model_prices))

    return None


def calculate_price_delta_percent(price: float, market_price: float) -> float:
    if market_price <= 0:
        return 0.0

    return ((price - market_price) / market_price) * 100


def classify_deal(price: float, market_price: float) -> str:
    delta_percent = calculate_price_delta_percent(price, market_price)

    if delta_percent < -35:
        return "suspicious"
    if delta_percent <= -20:
        return "great_deal"
    if delta_percent <= -10:
        return "good_price"
    if delta_percent <= 10:
        return "fair_price"
    return "overpriced"


def annotate_ranked_listings(listings: list[Listing], keyword: str) -> list[dict]:
    ranked_listings = rank_listings(listings, keyword)
    market_price = estimate_market_price(listings, keyword)
    target_model = get_target_model(keyword)
    annotated_listings: list[dict] = []

    for listing, score in ranked_listings:
        category = extract_category_from_url(listing.url)
        detected_model = extract_gpu_model(listing.title)
        model_match = is_exact_model_match(listing.title, keyword)
        variant_mismatch = is_model_variant_mismatch(listing.title, keyword)
        delta_percent = None
        deal_label = None

        if variant_mismatch:
            deal_label = "variant_mismatch"
        elif market_price is not None and model_match:
            delta_percent = calculate_price_delta_percent(listing.price, market_price)
            deal_label = classify_deal(listing.price, market_price)
        elif market_price is not None:
            deal_label = "not_comparable"

        annotated_listings.append(
            {
                "listing": listing,
                "score": score,
                "category": category,
                "detected_model": detected_model,
                "target_model": target_model,
                "model_match": model_match,
                "market_price": market_price,
                "delta_percent": delta_percent,
                "deal_label": deal_label,
            }
        )

    return annotated_listings
