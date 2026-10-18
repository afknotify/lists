import requests

# Set these to the values from your existing script.
BASE_URL = "https://your-server.example"
kind = "movie"
catalog_id = "your-catalog-id"

OUTPUT_FILE = "imdb_ids.txt"

session = requests.Session()
skip = 0
catalog_total = 0
imdb_ids = []

while True:
    # Use a query parameter (?skip=) instead of a path segment (/skip=).
    url = f"{BASE_URL.rstrip('/')}/catalog/{kind}/{catalog_id}.json?skip={skip}"

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        metas = data.get("metas", [])
    except Exception as e:
        print(f"\nError fetching {url}: {e}")
        break

    if not metas:
        break

    for meta in metas:
        item_id = meta.get("id", "")

        if isinstance(item_id, str) and item_id.startswith("tt") and item_id[2:].isdigit():
            imdb_ids.append(item_id)

    catalog_total += len(metas)
    skip += len(metas)
    print(f"({catalog_total} items...)", end=" ")

# Remove duplicates while preserving the original order.
unique_ids = list(dict.fromkeys(imdb_ids))

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    for imdb_id in unique_ids:
        file.write(f"{imdb_id}\n")

print(f"\nSaved {len(unique_ids)} IMDb IDs to {OUTPUT_FILE}")
