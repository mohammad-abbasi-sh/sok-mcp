"""Live tests — hit the real sokmarket.com.tr. Cautious: a few requests, then stop.

Run:  pytest tests/test_live.py -v
Skip: pytest -m "not live"  (or set SOK_SKIP_LIVE=1)
"""
import os
import pathlib
import sys
import time
import unittest

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from sok_mcp import http as _http
from sok_mcp import products as _P

pytestmark = pytest.mark.live
SKIP = os.environ.get("SOK_SKIP_LIVE") == "1"


@pytest.mark.skipif(SKIP, reason="SOK_SKIP_LIVE=1")
class TestLive(unittest.TestCase):
    def test_search_is_real(self):
        res = _P.parse_product_cards(_http.fetch_search("süt"))
        self.assertGreaterEqual(res["total"], 50)
        self.assertGreaterEqual(len(res["products"]), 10)
        self.assertTrue(all(p["price_try"] for p in res["products"]))
        print(f"\nLIVE search 'süt': {res['total']} products, "
              f"first = {res['products'][0]['title']} @ {res['products'][0]['price_try']}₺")
        time.sleep(1)

    def test_product_is_real(self):
        res = _P.parse_product_cards(_http.fetch_search("süt"))
        first = res["products"][0]
        page = _P.parse_product_page(_http.fetch_product(first["url"]))
        self.assertEqual(page["title"], first["title"])
        self.assertEqual(page["price_try"], first["price_try"])
        print(f"\nLIVE product: {page['title']} @ {page['price_try']}₺, "
              f"{len(page['related_products'])} related")
        time.sleep(1)

    def test_home_categories_are_real(self):
        cats = _P.parse_categories(_http.fetch_home())
        self.assertGreaterEqual(len(cats), 15)
        print(f"\nLIVE home: {len(cats)} categories, first = {cats[0]['name']}")
        time.sleep(1)

    def test_campaigns_are_real(self):
        promos = _P.parse_promotions(_http.fetch_campaigns())
        self.assertGreaterEqual(len(promos), 1)
        print(f"\nLIVE campaigns: {len(promos)} — {[p['name'] for p in promos]}")
        time.sleep(1)

    def test_category_page_is_real(self):
        res = _P.parse_product_cards(_http.fetch_category("sut-ve-sut-urunleri-c-460"))
        self.assertGreaterEqual(len(res["products"]), 10)
        print(f"\nLIVE category süt: {len(res['products'])} products on first page")
        time.sleep(1)


if __name__ == "__main__":
    unittest.main()
