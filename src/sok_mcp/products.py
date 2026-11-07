"""Domain logic: parse ŞOK (sokmarket.com.tr) pages into compact dicts.

Data sources (all public, no login, no key):
- search:   /arama?q=<query> — server-rendered product cards
  ("207 adet ürün listelendi"), title + price per card
- product:  /<slug>-p-<id> — h1 title, price, related products
- category: /<slug>-c-<id> — same product-card grid as search
- home:     / — 19 categories (-c- links) + promo groups (-pgrp-)
- promos:   /kampanyalar — campaign groups (-pgrp- links)
Prices are Turkish format ("43,50₺", thousands "1.234,56₺").
Stdlib parsing only (re / html).
"""
from __future__ import annotations

import html as _html
import re
import statistics

BASE = "https://www.sokmarket.com.tr"

_CARD_TITLE = "CProductCard-module_title__u8bMW"


def _clean(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", _html.unescape(str(text))).strip()


def parse_price(text: str | None) -> float | None:
    """'43,50' / '1.234,56' (Turkish) -> 43.5 / 1234.56."""
    if not text:
        return None
    s = text.strip().replace("₺", "").replace("\xa0", "").strip()
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _price_in(block: str) -> float | None:
    m = re.search(
        r'data-testid="(?:discountedPrice|price)">([\d.,]+)<!-- -->\s*₺', block
    )
    return parse_price(m.group(1)) if m else None


def parse_product_cards(html: str) -> dict:
    """Product-card grid -> {total, products[{title, slug, id, url, price_try}]}.

    total comes from the "N adet ürün listelendi" line when present.
    """
    total = None
    m = re.search(r"(\d+)(?:<!-- -->)?\s*adet ürün", html)
    if m:
        total = int(m.group(1))
    products, seen = [], set()
    # Each card is an <a href="/<slug>-p-<id>"> wrapping title + price.
    for link in re.finditer(r'<a href="(/[^"]+-p-(\d+))">', html):
        href, pid = link.group(1), link.group(2)
        if pid in seen:
            continue
        block = html[link.start(): link.start() + 4000]
        t = re.search(
            rf'<h2 class="{re.escape(_CARD_TITLE)}">(.*?)</h2>', block, re.S
        )
        if not t:
            continue
        seen.add(pid)
        products.append(
            {
                "title": _clean(t.group(1)),
                "slug": href.strip("/").rsplit("-p-", 1)[0],
                "id": pid,
                "url": f"{BASE}{href}",
                "price_try": _price_in(block),
            }
        )
    return {"total": total if total is not None else len(products), "products": products}


def parse_product_page(html: str) -> dict:
    """Product detail page: h1 title, price, related products."""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    title = _clean(re.sub(r"<[^>]+>", "", h1.group(1))) if h1 else ""
    if not title:
        raise ValueError("no product title found on this page")
    related = [
        _clean(t)
        for t in re.findall(
            rf'<h2 class="{re.escape(_CARD_TITLE)}">(.*?)</h2>', html, re.S
        )
    ]
    return {
        "title": title,
        "price_try": _price_in(html),
        "related_products": related,
    }


def parse_categories(html: str) -> list[dict]:
    """Homepage category links: /<slug>-c-<id> with Turkish link text."""
    out, seen = [], set()
    for href, _cid, inner in re.findall(
        r'<a[^>]+href="(/[^"]+-c-(\d+))"[^>]*>(.*?)</a>', html, re.S
    ):
        name = _clean(re.sub(r"<[^>]+>", "", inner))
        if not name or href in seen:
            continue
        seen.add(href)
        out.append(
            {
                "name": name,
                "slug": href.strip("/").rsplit("-c-", 1)[0],
                "id": href.rsplit("-c-", 1)[-1],
                "url": f"{BASE}{href}",
            }
        )
    return out


def parse_promotions(html: str) -> list[dict]:
    """Campaign groups: /<slug>-pgrp-<uuid> links with link text."""
    out, seen = [], set()
    for href, inner in re.findall(
        r'<a[^>]+href="(/[^"]+-pgrp-[^"]+)"[^>]*>(.*?)</a>', html, re.S
    ):
        name = _clean(re.sub(r"<[^>]+>", "", inner))
        if not name or href in seen:
            continue
        seen.add(href)
        out.append({"name": name, "slug": href.strip("/").rsplit("-pgrp-", 1)[0], "url": f"{BASE}{href}"})
    # The /kampanyalar page also links promos without inner text in some
    # spots; fall back to bare hrefs with a slug-derived name.
    if not out:
        for href in sorted(set(re.findall(r'href="(/[^"]+-pgrp-[^"]+)"', html))):
            slug = href.strip("/").rsplit("-pgrp-", 1)[0]
            out.append(
                {"name": slug.replace("-", " "), "slug": slug, "url": f"{BASE}{href}"}
            )
    return out


def price_stats(products: list[dict]) -> dict:
    """min / max / median / mean over products that have a price."""
    prices = sorted(p["price_try"] for p in products if p.get("price_try") is not None)
    if not prices:
        return {"count": 0, "min_try": None, "max_try": None, "median_try": None, "mean_try": None}
    return {
        "count": len(prices),
        "min_try": prices[0],
        "max_try": prices[-1],
        "median_try": statistics.median(prices),
        "mean_try": round(statistics.fmean(prices), 2),
    }
