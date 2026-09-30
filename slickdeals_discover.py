"""
Discovers current Home Depot clearance/penny deal threads on Slickdeals by
reading their published sitemap -- not their disallowed /search* or
/tag/* endpoints (robots.txt blocks both), and not a hardcoded thread
list, which goes stale fast (the original 4 hardcoded threads turned out
to be dead since January 2022 -- nobody had posted in any of them in
almost 4 years). Sitemaps are explicitly meant to be crawled (robots.txt
itself links this one), so this is the compliant way to find new threads
as they're posted, instead of guessing/hardcoding.

Slickdeals publishes ~10 "threads-weekly-N.xml.gz" sitemaps (confirmed
live 2026-09-30, most recently modified within the last day), each
listing tens of thousands of recent thread URLs. This downloads all of
them, filters for URLs whose slug mentions "home-depot" plus a
clearance-ish keyword (clearance/ymmv/penny/b-m), and caches the filtered
result locally so every collection run doesn't need to re-download ~19MB
of sitemap data -- only refreshed once the cache is older than
SITEMAP_CACHE_MAX_AGE_HOURS.
"""

from __future__ import annotations

import gzip
import json
import re
import time
from pathlib import Path

import requests

import config

SITEMAP_INDEX_URL = "https://slickdeals.net/attachment/sitemaps/sitemap.xml"
CACHE_FILE = Path(__file__).parent / "slickdeals_thread_cache.json"
SITEMAP_CACHE_MAX_AGE_HOURS = 12

_KEYWORD_RE = re.compile(r"clearance|ymmv|penny|b-m", re.IGNORECASE)
_SITEMAP_LOC_RE = re.compile(r"<loc>(.*?)</loc>")
_THREAD_URL_RE = re.compile(r"https://slickdeals\.net/f/(\d+)-[a-z0-9-]*home-depot[a-z0-9-]*", re.IGNORECASE)


def _thread_id(url: str) -> int:
    """Slickdeals thread ids increase over time, so this doubles as a
    recency sort key without needing to parse posted dates out of every
    candidate up front."""
    m = re.search(r"/f/(\d+)-", url)
    return int(m.group(1)) if m else 0


def _fetch(url: str) -> bytes:
    resp = requests.get(url, headers={"User-Agent": config.HTTP_USER_AGENT}, timeout=config.REQUEST_TIMEOUT_SECONDS)
    resp.raise_for_status()
    return resp.content


def _discover_weekly_sitemap_urls() -> list[str]:
    index_xml = _fetch(SITEMAP_INDEX_URL).decode("utf-8")
    return [loc for loc in _SITEMAP_LOC_RE.findall(index_xml) if "threads-weekly" in loc]


def _extract_matching_threads(sitemap_gz_url: str) -> list[str]:
    raw = _fetch(sitemap_gz_url)
    xml = gzip.decompress(raw).decode("utf-8", errors="ignore")
    return [m.group(0) for m in _THREAD_URL_RE.finditer(xml) if _KEYWORD_RE.search(m.group(0))]


def discover_threads(force_refresh: bool = False) -> list[str]:
    """Returns the current list of candidate Home Depot clearance/penny
    thread URLs, using a local cache (refreshed at most once every
    SITEMAP_CACHE_MAX_AGE_HOURS) so this doesn't re-download Slickdeals'
    full sitemap set on every single collection run."""
    if not force_refresh and CACHE_FILE.exists():
        cached = json.loads(CACHE_FILE.read_text())
        age_hours = (time.time() - cached["fetched_at"]) / 3600
        if age_hours < SITEMAP_CACHE_MAX_AGE_HOURS:
            return cached["urls"]

    weekly_urls = _discover_weekly_sitemap_urls()
    all_matches: set[str] = set()
    for sitemap_url in weekly_urls:
        try:
            all_matches.update(_extract_matching_threads(sitemap_url))
        except Exception as e:
            print(f"  Sitemap fetch failed for {sitemap_url}: {e}")

    urls = sorted(all_matches, key=_thread_id, reverse=True)  # newest threads first
    CACHE_FILE.write_text(json.dumps({"fetched_at": time.time(), "urls": urls}))
    return urls


if __name__ == "__main__":
    threads = discover_threads(force_refresh=True)
    print(f"Found {len(threads)} candidate Home Depot clearance thread(s):")
    for t in threads:
        print(f"  {t}")
