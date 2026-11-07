# sok-mcp 🇹🇷

**ŞOK** (sokmarket.com.tr) için gayriresmî, **salt-okunur** MCP sunucusu — Türkiye'nin büyük indirim market zincirlerinden biri: ürün arama, ürün detayı, kategoriler, kampanya grupları ve fiyat istatistikleri.

> "Türkiye MCP fabrikası" parçası (Sepehr tarzı pipeline). ŞOK ile bağlantısı yoktur.

## Yapay zekâ ajanları için

MCP istemcinize ekleyin (stdio):

```json
{
  "mcpServers": {
    "sok": {
      "command": "uvx",
      "args": ["sok-mcp"]
    }
  }
}
```

## Araçlar

| Araç | Açıklama |
|------|----------|
| `sok_search_products` | İsme göre ürün ara — `query`, `limit` (1..30, yalnızca ilk sayfa) |
| `sok_get_product` | Ürün detayı — `slug_or_url` (örn. `...-p-320230` veya tam sokmarket.com.tr URL'si) |
| `sok_list_categories` | Mağaza kategorileri (ad, slug, id, url) |
| `sok_category_products` | Bir kategorideki ürünler — `category` slug veya URL, `limit` (1..30) |
| `sok_list_promotions` | Güncel kampanya grupları (`/kampanyalar`) |
| `sok_price_stats` | Bir aramanın fiyat istatistikleri — adet, min, max, medyan, ortalama (TRY) |

Örnek (`sok_search_products` / "süt"): 207 ürün; ilk sonuç "Mis Uht Süt Yarım Yağlı 1 L" — 43,50₺. Örnek (`sok_price_stats` / "süt"): ilk sayfada 10 ürün, min 16,50₺, max 88,50₺, medyan 55,75₺.

Notlar:
- Fiyatlar Türk Lirası (TRY); site Türkçe yazar (`43,50₺`).
- Arama/kategori sayfaları ilk sayfayı döner (~20 ürün); `total` tüm eşleşmeleri bildirir.
- Veri: sokmarket.com.tr herkese açık sayfalar — giriş yok, API anahtarı yok, salt-okunur.

## Kurallar

Gayriresmî ve salt-okunur — giriş yok, API anahtarı yok, yazma yok. Testler: çevrimdışı fixture + canlı testler (15/15 yeşil).
