# import necessary libraries
import requests
import feedparser
import pandas as pd
import os
import time
os.makedirs("data", exist_ok=True)

# Settings
URL = "http://export.arxiv.org/api/query"
QUERY = "cat:stat.ML AND submittedDate:[202511260000 TO 202611260000]"
PAGE = 1000

def get_page(params):
    wait = 10
    for attempt in range(5):
        response = requests.get(URL, params=params, timeout=60)
        if response.status_code == 429:
            print(f"Rate limited, waiting {wait}s...")
            time.sleep(wait)
            wait *= 2              # 10, 20, 40, 80...
            continue
        response.raise_for_status()
        return feedparser.parse(response.content)
    raise RuntimeError("Still rate limited after 5 tries")

# Fetch papers from arXiv API
params = {
    "search_query": QUERY,
    "start": 0,
    "max_results": 1,
    "sortBy": "submittedDate",
    "sortOrder": "descending",
}
feed = get_page(params)                       # ← here
total = int(feed.feed.opensearch_totalresults)
print("Total results:", total)
time.sleep(3)

print(pd.read_csv("data/papers.csv").head())

rows = []
for start in range(0, total, PAGE):
    params["start"] = start
    params["max_results"] = PAGE
    feed = get_page(params)
    for entry in feed.entries:
        rows.append({
            "id": entry.id.replace("http://arxiv.org/abs/", ""),
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "abstract": entry.summary,
            "primary_category": entry.arxiv_primary_category["term"],
            "categories": ";".join(t["term"] for t in entry.tags),
        })
    print(f"Got {start} to {start + PAGE}")
    time.sleep(3)

df = pd.DataFrame(rows)
df = df.drop_duplicates(subset="id")
df.to_csv("data/papers.csv", index=False)
print("Saved", len(df), "papers")
print("Earliest:", df["published"].min())
print("Latest:", df["published"].max())