"""MCP server: unofficial read-only access to ŞOK grocery (sokmarket.com.tr)."""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from . import http as _http
from . import products as _P

mcp = FastMCP("sok-mcp")

INSTRUCTIONS = """\
Unofficial read-only MCP server for ŞOK (sokmarket.com.tr), one of \
Türkiye's big discount grocery chains — product search, product \
details, categories, campaign groups and price statistics. All \
pages are server-rendered Next.js with no login and no API key; \
prices are in Turkish Lira (TRY, Turkish format "43,50₺"). \
Search/category pages list the first page of results (~20 \
products); the `total` field reports how many products matched \
overall. Read-only; transport uses Chrome TLS impersonation with \
a plain-requests fallback; requests are spaced ~0.8s apart. Built \
by Mohammad Abbasi (mohammad-abbasi-sh) — Turkey MCP factory.\
Built by Mohammad Abbasi (mohammad-abbasi-sh) — https://almanibama.ir · https://mabbasi.ir
"""


def _err(e: Exception) -> str:
    return json.dumps({"error": str(e)}, ensure_ascii=False)


def _validate_limit(limit: int, lo: int = 1, hi: int = 30) -> int:
    if not lo <= limit <= hi:
        raise ValueError(f"limit must be between {lo} and {hi}")
    return limit


@mcp.tool()
def sok_search_products(query: str, limit: int = 20) -> str:
    """Search ŞOK products by name.
    query: e.g. "süt", "çay", "peynir". limit 1..30 (first page only;
    `total` reports all matches). Returns title, slug, id, url and
    price in TRY per product."""
    try:
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        _validate_limit(limit)
        res = _P.parse_product_cards(_http.fetch_search(query.strip()))
    except (ValueError, _http.SokError) as e:
        return _err(e)
    res["products"] = res["products"][:limit]
    return json.dumps({"query": query.strip(), **res}, ensure_ascii=False)


@mcp.tool()
def sok_get_product(slug_or_url: str) -> str:
    """Product detail: title, price in TRY, related products.
    slug_or_url: e.g. "ahmad-tea-classic-earl-grey-demlik-poset-40-li-p-320230"
    or a full sokmarket.com.tr product URL."""
    try:
        s = slug_or_url.strip()
        if not s:
            raise ValueError("slug_or_url must not be empty")
        page = _P.parse_product_page(_http.fetch_product(s))
    except (ValueError, _http.SokError) as e:
        return _err(e)
    return json.dumps({"url": slug_or_url.strip(), **page}, ensure_ascii=False)


@mcp.tool()
def sok_list_categories() -> str:
    """ŞOK store categories (name, slug, id, url) from the homepage."""
    try:
        cats = _P.parse_categories(_http.fetch_home())
    except (ValueError, _http.SokError) as e:
        return _err(e)
    return json.dumps({"count": len(cats), "categories": cats}, ensure_ascii=False)


@mcp.tool()
def sok_category_products(category: str, limit: int = 20) -> str:
    """Products in one ŞOK category.
    category: slug like "sut-ve-sut-urunleri-c-460" or a full
    sokmarket.com.tr category URL. limit 1..30 (first page only)."""
    try:
        if not category or not category.strip():
            raise ValueError("category must not be empty")
        _validate_limit(limit)
        res = _P.parse_product_cards(_http.fetch_category(category.strip()))
    except (ValueError, _http.SokError) as e:
        return _err(e)
    res["products"] = res["products"][:limit]
    return json.dumps({"category": category.strip(), **res}, ensure_ascii=False)


@mcp.tool()
def sok_list_promotions() -> str:
    """Current ŞOK campaign groups from /kampanyalar
    (name, slug, url — each links to its discounted products)."""
    try:
        promos = _P.parse_promotions(_http.fetch_campaigns())
    except (ValueError, _http.SokError) as e:
        return _err(e)
    return json.dumps({"count": len(promos), "promotions": promos}, ensure_ascii=False)


@mcp.tool()
def sok_price_stats(query: str) -> str:
    """Price statistics for a search: count, min, max, median, mean in
    TRY over the first results page. query: e.g. "süt"."""
    try:
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        res = _P.parse_product_cards(_http.fetch_search(query.strip()))
        stats = _P.price_stats(res["products"])
    except (ValueError, _http.SokError) as e:
        return _err(e)
    return json.dumps(
        {"query": query.strip(), "total_matches": res["total"], **stats},
        ensure_ascii=False,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    import sys

    sys.exit(main())
