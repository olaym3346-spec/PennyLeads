"""
Reddit collection -- NOT active by default.

Reddit's own robots.txt hard-blocks anonymous/unauthenticated requests
(confirmed live 2026-09-30: even fetching robots.txt itself returned an
explicit block page -- "whoa there, pardner!" -- telling scripts to
register at https://www.reddit.com/prefs/apps), so this uses PRAW (the
official Python Reddit API wrapper) with real OAuth credentials instead of
trying to scrape around that block.

One-time setup (free, ~2 minutes):
  1. Log into Reddit, go to https://www.reddit.com/prefs/apps
  2. Click "create app" -- choose type "script"
  3. Name/description can be anything; redirect uri can be
     http://localhost:8080
  4. Copy the client id (shown under the app's name) and secret into
     config.py's REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET
  5. Set config.REDDIT_USER_AGENT to something descriptive and unique,
     e.g. "pennyleads-script/0.1 by u/<your-reddit-username>" -- Reddit
     rejects generic/empty user agents
  6. pip install praw

Once REDDIT_CLIENT_ID is non-empty, collect_leads.py picks this up
automatically.
"""

from __future__ import annotations

import config


def fetch_reddit_leads() -> list[tuple[str, str | None, str, str]]:
    """Returns (source_url, author, posted_at, text) tuples from
    searching config.REDDIT_SUBREDDITS for config.REDDIT_SEARCH_QUERY --
    both matching submissions and their comments."""
    import praw

    reddit = praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_CLIENT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
    )

    leads = []
    for sub_name in config.REDDIT_SUBREDDITS:
        subreddit = reddit.subreddit(sub_name)
        for submission in subreddit.search(config.REDDIT_SEARCH_QUERY, sort="new", limit=25):
            leads.append((
                f"https://www.reddit.com{submission.permalink}",
                str(submission.author) if submission.author else None,
                str(submission.created_utc),
                f"{submission.title}\n{submission.selftext}".strip(),
            ))
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                leads.append((
                    f"https://www.reddit.com{comment.permalink}",
                    str(comment.author) if comment.author else None,
                    str(comment.created_utc),
                    comment.body,
                ))
    return leads


if __name__ == "__main__":
    if not config.REDDIT_CLIENT_ID:
        raise SystemExit("REDDIT_CLIENT_ID is not set in config.py -- see this file's docstring for setup steps.")
    for lead in fetch_reddit_leads():
        print(lead)
