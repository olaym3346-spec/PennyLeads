"""
Main entry point: fetches every configured Slickdeals thread (and Reddit,
once config.REDDIT_CLIENT_ID etc. are filled in -- see reddit_scraper.py)
and logs any new comments into penny_leads.db.

Collect-only -- no Home Depot requests, no verification, no alerting. The
point right now is comparing what these community sources are reporting
against what Penny3's own category-crawl finds on its own, before
deciding whether/how to wire live verification in.

Usage:
    python collect_leads.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import config
from leads_db import get_conn, insert_lead
from slickdeals_discover import discover_threads
from slickdeals_scraper import fetch_thread_comments

ROTATION_STATE_FILE = Path(__file__).parent / "slickdeals_rotation_state.json"


def _candidate_threads() -> list[str]:
    discovered = discover_threads()
    # config.SEED_THREAD_URLS first (always included), then discovered
    # threads not already in that list, so a manual seed never gets
    # crowded out by rotation.
    seen = set(config.SEED_THREAD_URLS)
    return list(config.SEED_THREAD_URLS) + [u for u in discovered if u not in seen]


def _next_chunk(candidates: list[str], chunk_size: int) -> list[str]:
    total = len(candidates)
    if total == 0:
        return []
    chunk_size = min(chunk_size, total)
    try:
        start = json.loads(ROTATION_STATE_FILE.read_text())["next_offset"] % total
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        start = 0
    chunk = [candidates[(start + i) % total] for i in range(chunk_size)]
    ROTATION_STATE_FILE.write_text(json.dumps({"next_offset": (start + chunk_size) % total}))
    return chunk


def run_slickdeals(conn) -> tuple[int, int]:
    candidates = _candidate_threads()
    urls = _next_chunk(candidates, config.SLICKDEALS_THREADS_PER_RUN)
    print(f"{len(candidates)} candidate thread(s) known; fetching {len(urls)} this run.")

    seen = 0
    new = 0
    for i, url in enumerate(urls):
        print(f"Fetching {url} ...")
        try:
            comments = fetch_thread_comments(url)
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        thread_new = 0
        for c in comments:
            seen += 1
            if insert_lead(conn, "slickdeals", url, c["author"], c["posted_at"], c["text"]):
                new += 1
                thread_new += 1
        print(f"  {len(comments)} comment(s) seen, {thread_new} new.")

        if i < len(urls) - 1:
            time.sleep(config.REQUEST_DELAY_SECONDS)
    return seen, new


def run_reddit(conn) -> tuple[int, int]:
    if not config.REDDIT_CLIENT_ID:
        print("Reddit skipped -- no REDDIT_CLIENT_ID configured (see reddit_scraper.py for setup).")
        return 0, 0

    from reddit_scraper import fetch_reddit_leads

    seen = 0
    new = 0
    for source_url, author, posted_at, text in fetch_reddit_leads():
        seen += 1
        if insert_lead(conn, "reddit", source_url, author, posted_at, text):
            new += 1
    return seen, new


def main():
    conn = get_conn()
    sd_seen, sd_new = run_slickdeals(conn)
    rd_seen, rd_new = run_reddit(conn)
    conn.close()
    print(f"\nDone. Slickdeals: {sd_seen} seen / {sd_new} new. Reddit: {rd_seen} seen / {rd_new} new.")


if __name__ == "__main__":
    main()
