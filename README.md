# sok-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/sok-mcp

Unofficial **read-only** MCP server for **ŞOK** (sokmarket.com.tr) — one of Türkiye's big discount grocery chains: product search, product details, categories, campaign groups and price statistics.

> Part of the "Turkey MCP factory" (Sepehr-style pipeline). Not affiliated with ŞOK.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "sok": {
      "command": "uvx",
      "args": ["sok-mcp==0.1.1"]
    }
  }
}
```

Or run locally: `python -m sok_mcp.server` (needs `mcp<2`, `curl-cffi`, `requests`).

## Tools

| Tool | Description |
|------|-------------|
| `sok_search_products` | Search products by name — `query`, `limit` (1..30, first page only) |
| `sok_get_product` | Product detail — `slug_or_url` (e.g. `...-p-320230` or a full sokmarket.com.tr URL) |
| `sok_list_categories` | Store categories (name, slug, id, url) |
| `sok_category_products` | Products in one category — `category` slug or URL, `limit` (1..30) |
| `sok_list_promotions` | Current campaign groups from `/kampanyalar` |
| `sok_price_stats` | Price stats for a search — count, min, max, median, mean in TRY |

Example output (`sok_search_products` / "süt"):

```json
{"query": "süt", "total": 207,
 "products": [{"title": "Mis Uht Süt Yarım Yağlı 1 L", "id": "5834",
   "url": "https://www.sokmarket.com.tr/mis-uht-sut-yarim-yagli-1-l-p-5834",
   "price_try": 43.5}]}
```

Example output (`sok_price_stats` / "süt", first page of 10):

```json
{"query": "süt", "total_matches": 207, "count": 10,
 "min_try": 16.5, "max_try": 88.5, "median_try": 55.75, "mean_try": 52.05}
```

Notes:
- Prices are Turkish Lira (TRY); the site writes them Turkish-style (`43,50₺`).
- Search/category pages return the first page (~20 products); `total` reports all matches.
- Data: sokmarket.com.tr public server-rendered pages — no key, no login, read-only.

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" curl-cffi requests pytest
.venv/bin/python -m pytest tests/ -q
```

- `tests/test_products.py` — offline, parses real captured fixtures
- `tests/test_live.py` — 5 cautious live requests against sokmarket.com.tr

## License

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
