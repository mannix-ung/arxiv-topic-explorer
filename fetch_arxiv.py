import requests
import feedparser
import pandas as pd
import os
os.makedirs("data", exist_ok=True)

URL = "http://export.arxiv.org/api/query"

params = {
    "search_query": "cat:stat.ML",
    "start": 0,
    "max_results": 10,
    "sortBy": "submittedDate",
    "sortOrder": "descending"}

response = requests.get(URL, params=params, timeout=60)
response.raise_for_status()

feed = feedparser.parse(response.content)
print("Total results", feed.feed.opensearch_totalresults)

first = feed.entries[0]
print(first.keys())

rows = []
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

os.makedirs("data", exist_ok=True)
pd.DataFrame(rows).to_csv("data/papers.csv", index=False)
print(pd.read_csv("data/papers.csv").head())