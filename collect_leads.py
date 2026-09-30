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

import time

import config
from leads_db import get_conn, insert_lead
from slickdeals_scraper import fetch_thread_comments


def run_slickdeals(conn) -> tuple[int, int]:
    seen = 0
    new = 0
    for i, url in enumerate(config.SLICKDEALS_THREAD_URLS):
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

        if i < len(config.SLICKDEALS_THREAD_URLS) - 1:
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
