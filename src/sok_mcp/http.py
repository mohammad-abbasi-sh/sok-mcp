"""HTTP layer for sok_mcp.

sokmarket.com.tr is a Next.js storefront that serves its search,
category and product pages fully server-rendered with no login and
no API key. Transport uses curl-cffi chrome120 impersonation (the
proven Turkey-factory pattern) with a plain-requests fallback.
Requests are kept gentle (one at a time, ~0.8s apart) and read-only.
"""
from __future__ import annotations

import time
from urllib.parse import quote

from curl_cffi import requests as _creq
import requests as _plain

BASE = "https://www.sokmarket.com.tr"
TIMEOUT = 30.0
MIN_INTERVAL = 0.8  # seconds between requests — be polite

_HEADERS = {
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

_last_fetch = 0.0


class SokError(RuntimeError):
    pass


def _throttle() -> None:
    global _last_fetch
    wait = MIN_INTERVAL - (time.monotonic() - _last_fetch)
    if wait > 0:
        time.sleep(wait)
    _last_fetch = time.monotonic()


def _get(url: str) -> str:
    _throttle()
    try:
        resp = _creq.get(url, impersonate="chrome120", headers=_HEADERS, timeout=TIMEOUT)
        status, text = resp.status_code, resp.text
    except Exception:
        # Fallback transport: plain requests with a browser UA.
        try:
            resp = _plain.get(url, headers={**_HEADERS, "User-Agent": _UA}, timeout=TIMEOUT)
            status, text = resp.status_code, resp.text
        except Exception as e:
            raise SokError(f"network error fetching {url}: {e}") from e
    if status == 403:
        raise SokError(
            "sokmarket.com.tr refused the request (HTTP 403, bot wall) — try again later"
        )
    if status == 429:
        raise SokError(
            "sokmarket.com.tr rate-limited the request (HTTP 429) — try again later"
        )
    if status == 404:
        raise SokError(f"sokmarket.com.tr has no page at {url} (HTTP 404)")
    if status != 200:
        raise SokError(f"sokmarket.com.tr returned HTTP {status} for {url}")
    return text


def fetch_search(query: str) -> str:
    return _get(f"{BASE}/arama?q={quote(query)}")


def fetch_product(path: str) -> str:
    path = path.strip()
    if path.startswith("http"):
        return _get(path)
    return _get(f"{BASE}/{path.lstrip('/')}")


def fetch_home() -> str:
    return _get(f"{BASE}/")


def fetch_category(path: str) -> str:
    return _get(f"{BASE}/{path.strip().lstrip('/')}")


def fetch_campaigns() -> str:
    return _get(f"{BASE}/kampanyalar")
