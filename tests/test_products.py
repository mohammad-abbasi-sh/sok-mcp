"""Offline tests — parse real captured ŞOK fixtures, no network."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from sok_mcp import products as P

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"


class TestSearchCards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res = P.parse_product_cards((FIX / "search.html").read_text(encoding="utf-8"))

    def test_total(self):
        self.assertEqual(self.res["total"], 207)

    def test_card_count_and_first(self):
        self.assertEqual(len(self.res["products"]), 10)
        first = self.res["products"][0]
        self.assertEqual(first["title"], "Mis Uht Süt Yarım Yağlı 1 L")
        self.assertEqual(first["id"], "5834")
        self.assertEqual(first["price_try"], 43.5)
        self.assertTrue(first["url"].endswith("-p-5834"))

    def test_prices(self):
        by_id = {p["id"]: p for p in self.res["products"]}
        self.assertEqual(by_id["7796"]["price_try"], 88.5)
        self.assertEqual(by_id["5179"]["price_try"], 36.0)

    def test_stats(self):
        s = P.price_stats(self.res["products"])
        self.assertEqual(s["count"], 10)
        self.assertEqual(s["min_try"], 16.5)
        self.assertEqual(s["max_try"], 88.5)
        self.assertEqual(s["median_try"], 55.75)
        self.assertEqual(s["mean_try"], 52.05)

    def test_empty_stats(self):
        self.assertEqual(P.price_stats([])["count"], 0)
        self.assertIsNone(P.price_stats([])["min_try"])


class TestProductPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = P.parse_product_page((FIX / "product.html").read_text(encoding="utf-8"))

    def test_title_and_price(self):
        self.assertEqual(self.p["title"], "Ahmad Tea Classic Earl Grey Demlik Poşet 40'lı")
        self.assertEqual(self.p["price_try"], 149.0)

    def test_no_title_raises(self):
        with self.assertRaises(ValueError):
            P.parse_product_page("<html><body>no h1</body></html>")


class TestHomeAndCampaigns(unittest.TestCase):
    def test_categories(self):
        cats = P.parse_categories((FIX / "home.html").read_text(encoding="utf-8"))
        self.assertEqual(len(cats), 19)
        by_id = {c["id"]: c for c in cats}
        self.assertEqual(by_id["460"]["name"], "Süt & Süt Ürünleri")
        self.assertEqual(by_id["20"]["slug"], "meyve-ve-sebze")

    def test_promotions(self):
        promos = P.parse_promotions((FIX / "kampanyalar.html").read_text(encoding="utf-8"))
        self.assertEqual(len(promos), 2)
        names = [p["name"] for p in promos]
        self.assertIn("Kazandırır Alışverişin", names)
        self.assertIn("Kasa Arkası Ürünler", names)

    def test_price_parsing(self):
        self.assertEqual(P.parse_price("43,50"), 43.5)
        self.assertEqual(P.parse_price("1.234,56"), 1234.56)
        self.assertIsNone(P.parse_price("fiyat yok"))
        self.assertIsNone(P.parse_price(None))


if __name__ == "__main__":
    unittest.main()
