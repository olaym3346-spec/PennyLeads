"""
Template for config.py -- copy this file to config.py and fill in your
own Reddit credentials there. config.py is gitignored specifically so
real credentials never end up committed; this example file (with empty
placeholders) is what's tracked in git instead.
"""

HTTP_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
REQUEST_TIMEOUT_SECONDS = 20
REQUEST_DELAY_SECONDS = 4.0  # politeness delay between thread fetches

# Slickdeals thread discovery is dynamic now, via slickdeals_discover.py's
# sitemap-based search -- the original 4 hardcoded thread URLs here turned
# out to be dead (no posts since January 2022) the first time anyone
# actually checked their dates. Keep this as a manual seed list for any
# specific threads worth always including regardless of what the sitemap
# search turns up; empty is fine.
SEED_THREAD_URLS: list[str] = []

# How many discovered (+ seed) threads to actually fetch comments for per
# collection run -- caps request volume the same way Penny3 caps its
# category crawl, since the sitemap search alone can turn up hundreds of
# matching threads. Rotates through the full candidate list across runs
# (state in slickdeals_rotation_state.json) rather than always hitting the
# same first N.
SLICKDEALS_THREADS_PER_RUN = 20

# Reddit access requires a real, registered/approved API app -- see
# reddit_scraper.py's docstring for setup. Until these are filled in (in
# your local config.py, NOT this template), collect_leads.py skips Reddit
# entirely and only runs Slickdeals.
REDDIT_CLIENT_ID = ""
REDDIT_CLIENT_SECRET = ""
REDDIT_USER_AGENT = ""  # Reddit requires something descriptive+unique, e.g. "pennyleads-script/0.1 by u/<your-username>"
REDDIT_SUBREDDITS = ["Frugal", "homedepot"]  # no dedicated penny-hunting subreddit turned up in research -- adjust as leads come in
REDDIT_SEARCH_QUERY = "home depot penny"
