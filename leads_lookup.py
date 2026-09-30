"""
Terminal-only way to browse penny_leads.db.

Usage:
    python leads_lookup.py
        Lists the most recent leads across all sources.

    python leads_lookup.py --keyword penny
        Only leads whose text mentions this (case-insensitive substring).

    python leads_lookup.py --source slickdeals
        Only leads from this source.
"""

from __future__ import annotations

import argparse

from leads_db import get_conn


def list_leads(keyword: str | None = None, source: str | None = None, limit: int = 50):
    conn = get_conn()
    where = []
    params: list[str] = []
    if keyword:
        where.append("text LIKE ?")
        params.append(f"%{keyword}%")
    if source:
        where.append("source = ?")
        params.append(source)
    where_clause = f"WHERE {' AND '.join(where)}" if where else ""

    rows = conn.execute(
        f"""
        SELECT source, thread_url, author, posted_at, text, scraped_at
        FROM leads
        {where_clause}
        ORDER BY scraped_at DESC
        LIMIT ?
        """,
        (*params, limit),
    ).fetchall()
    conn.close()

    if not rows:
        print("No leads found.")
        return

    for source, thread_url, author, posted_at, text, scraped_at in rows:
        print(f"[{source}] {posted_at or '?'}  by {author or '?'}  (scraped {scraped_at})")
        print(f"    {text[:200]}")
        print(f"    {thread_url}")
        print()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--keyword", help="Only show leads whose text contains this (case-insensitive substring).")
    parser.add_argument("--source", choices=["slickdeals", "reddit"], help="Only show leads from this source.")
    parser.add_argument("--limit", type=int, default=50, help="Max rows to show (default 50).")
    args = parser.parse_args()
    list_leads(args.keyword, args.source, args.limit)


if __name__ == "__main__":
    main()
