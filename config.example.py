"""
Template for config.py -- copy this file to config.py and fill in your
own Reddit credentials there. config.py is gitignored specifically so
real credentials never end up committed; this example file (with empty
placeholders) is what's tracked in git instead.
"""

HTTP_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
REQUEST_TIMEOUT_SECONDS = 20
REQUEST_DELAY_SECONDS = 4.0  # politeness delay between thread fetches

# Known Slickdeals forum threads dedicated to Home Depot in-store
# clearance/penny finds -- found via a normal web search, not Slickdeals'
# own search endpoint (that path -- /search* -- is disallowed in their
# robots.txt; these direct thread URLs are not).
SLICKDEALS_THREAD_URLS = [
    "https://slickdeals.net/f/15635632-home-depot-clearance-deals-in-store-only-ymmv",
    "https://slickdeals.net/f/7735565-dedicated-thread-home-depot-b-m-ymmv-clearances-xx-06-xx-03-1-cent-deals-and-other-significant-discounts",
    "https://slickdeals.net/f/10387768-home-depot-yellow-clearance-tag-party-b-m-ymmv",
    "https://slickdeals.net/f/15589936-ymmv-home-depot-clearance-vanity-light-fixtures-0-01-in-store-only",
]

# Reddit access requires a real, registered/approved API app -- see
# reddit_scraper.py's docstring for setup. Until these are filled in (in
# your local config.py, NOT this template), collect_leads.py skips Reddit
# entirely and only runs Slickdeals.
REDDIT_CLIENT_ID = ""
REDDIT_CLIENT_SECRET = ""
REDDIT_USER_AGENT = ""  # Reddit requires something descriptive+unique, e.g. "pennyleads-script/0.1 by u/<your-username>"
REDDIT_SUBREDDITS = ["Frugal", "homedepot"]  # no dedicated penny-hunting subreddit turned up in research -- adjust as leads come in
REDDIT_SEARCH_QUERY = "home depot penny"
