import requests
from datetime import datetime

BASE_URL = "https://dracid-lists-addon.dracid.workers.dev/c/cmVsZWFzZWQtbW92aWVzfnJlbGVhc2VkLXNlcmllcw"
SITE_URL = "https://afknotify.github.io/lists/"

def escape_xml(text):
    """Convert special characters to XML-safe entities."""
    if not text:
        return ""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

session = requests.Session()
print("Fetching manifest...")
manifest = session.get(f"{BASE_URL}/manifest.json", timeout=30).json()

data_by_kind = {
    "movie": [],
    "series": [],
}
KIND_MAP = {
    "movie": "movie",
    "series": "series",
    "tv": "series" 
}

catalogs = manifest.get("catalogs", [])
print(f"Found {len(catalogs)} total catalogs in manifest.")

for catalog in catalogs:
    raw_kind = catalog["type"]
    
    kind = KIND_MAP.get(raw_kind)
    if not kind:
        print(f"Skipping unknown catalog type: {raw_kind}")
        continue

    catalog_id = catalog["id"]
    print(f"Processing {kind} catalog: {catalog_id}...", end=" ")
    
    skip = 0
    catalog_total = 0

    while True:
        suffix = "" if skip == 0 else f"/skip={skip}"
        url = f"{BASE_URL}/catalog/{kind}/{catalog_id}{suffix}.json"
        
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            metas = response.json().get("metas", [])
        except Exception as e:
            print(f"\nError fetching {url}: {e}")
            break

        if not metas:
            break

        for meta in metas:
            item_id = meta.get("id", "")
            if item_id.startswith("tt") and item_id[2:].isdigit():
                data_by_kind[kind].append({
                    "id": item_id,
                    "title": meta.get("name", item_id)
                })

        catalog_total += len(metas)
        skip += len(metas)
        print(f"({catalog_total} items...)", end=" ")

    print(f"Done. Total: {catalog_total}")

def generate_rss(kind, items, filename):
    seen = set()
    unique_items = []
    for item in items:
        if item["id"] not in seen:
            unique_items.append(item)
            seen.add(item["id"])

    rss_items = ""
    for item in unique_items:
        safe_title = escape_xml(item['title'])
        rss_items += f"""
        <item>
            <title>{safe_title}</title>
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
    print(f"Successfully saved {len(unique_items)} unique {kind} items to {filename}")

# Generate the files
generate_rss("movie", data_by_kind["movie"], "movies.xml")
generate_rss("series", data_by_kind["series"], "series.xml")
