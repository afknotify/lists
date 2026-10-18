import requests
from datetime import datetime

# Configuration
BASE_URL = "https://dracid-lists-addon.dracid.workers.dev/c/cmVsZWFzZWQtbW92aWVzfnJlbGVhc2VkLXNlcmllcw"
SITE_URL = "https://afknotify.github.io/lists/"

session = requests.Session()
manifest = session.get(f"{BASE_URL}/manifest.json", timeout=30).json()

data_by_kind = {
    "movie": [],
    "series": [],
}

for catalog in manifest.get("catalogs", []):
    kind = catalog["type"]
    if kind not in data_by_kind:
        continue

    catalog_id = catalog["id"]
    skip = 0

    while True:
        suffix = "" if skip == 0 else f"/skip={skip}"
        url = f"{BASE_URL}/catalog/{kind}/{catalog_id}{suffix}.json"
        response = session.get(url, timeout=30)
        response.raise_for_status()
        metas = response.json().get("metas", [])

        if not metas:
            break

        for meta in metas:
            item_id = meta.get("id", "")
            if item_id.startswith("tt") and item_id[2:].isdigit():
                data_by_kind[kind].append({
                    "id": item_id,
                    "title": meta.get("name", item_id)
                })

        skip += len(metas)

def generate_rss(kind, items, filename):
    # Remove duplicates while preserving order
    seen = set()
    unique_items = []
    for item in items:
        if item["id"] not in seen:
            unique_items.append(item)
            seen.add(item["id"])

    rss_items = ""
    for item in unique_items:
        rss_items += f"""
        <item>
            <title>{item['title']}</title>
            <link>https://www.imdb.com/title/{item['id']}/</link>
            <guid>https://www.imdb.com/title/{item['id']}/</guid>
            <description>IMDb ID: {item['id']}</description>
        </item>"""

    rss_content = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>{kind.capitalize()} List</title>
    <link>{SITE_URL}</link>
    <description>Automatically updated list of {kind}s</description>
    <lastBuildDate>{datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
    {rss_items}
</channel>
</rss>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(rss_content)
    print(f"Saved {len(unique_items)} {kind} items to {filename}")

# Generate the files
generate_rss("movie", data_by_kind["movie"], "movies.xml")
generate_rss("series", data_by_kind["series"], "series.xml")
