"""
Scrapes public Slickdeals forum threads (see config.SLICKDEALS_THREAD_URLS)
for comments -- read-only, no login, no posting. Only fetches specific
known thread URLs found via a normal web search, never Slickdeals' own
search endpoint (robots.txt disallows /search*; direct thread pages are
not disallowed).

Page structure confirmed live against a real fetched thread (checked
2026-09-30): each comment's body text sits in a
div.commentContentHtmlBlock. There's no single wrapper class tying author,
timestamp, and body together directly, so this walks up from the body to
the nearest ancestor that also contains a
.commentsThreadedCommentV2__author link and a .slickdealsTimestamp span --
that's the comment's container. Quote-echo blocks (the auto-rendered copy
of whatever text a reply is quoting, which Slickdeals renders as its own
commentContentHtmlBlock starting with "Quote from <name>:") are filtered
out since that text already exists as its own original comment elsewhere
on the page.
"""

from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

import config

_QUOTE_ECHO_RE = re.compile(r"^Quote\s*\n?\s*from\s", re.IGNORECASE)


def _find_comment_container(body_tag, max_levels: int = 15):
    node = body_tag
    for _ in range(max_levels):
        node = node.parent
        if node is None:
            return None
        if node.select_one(".commentsThreadedCommentV2__author") and node.select_one(".slickdealsTimestamp"):
            return node
    return None


def fetch_thread_comments(url: str) -> list[dict]:
    """Returns [{author, posted_at, text}, ...] for every real (non-quote-
    echo) comment on this thread page."""
    resp = requests.get(
        url,
        headers={"User-Agent": config.HTTP_USER_AGENT},
        timeout=config.REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    comments = []
    for body in soup.select(".commentContentHtmlBlock"):
        text = body.get_text(" ", strip=True)
        if not text or _QUOTE_ECHO_RE.match(text):
            continue
        container = _find_comment_container(body)
        author_tag = container.select_one(".commentsThreadedCommentV2__author") if container else None
        ts_tag = container.select_one(".slickdealsTimestamp") if container else None
        comments.append({
            "author": author_tag.get_text(strip=True) if author_tag else None,
            "posted_at": ts_tag.get("title") if ts_tag else None,
            "text": text,
        })
    return comments


if __name__ == "__main__":
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else config.SLICKDEALS_THREAD_URLS[0]
    for c in fetch_thread_comments(url):
        print(c)
