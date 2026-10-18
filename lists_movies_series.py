from pathlib import Path

import requests


# Use the API base URL from your existing script.
BASE_URL = "https://your-api-base-url"

# Replace the catalog IDs with the ones from your existing script.
# Keep the `kind` values exactly as your API expects.
CATALOGS = [
    {"kind": "series", "catalog_id": "YOUR_SERIES_CATALOG_ID"},
    {"kind": "movie", "catalog_id": "YOUR_MOVIES_CATALOG_ID"},
]

# Assumes this script is in the root of the directory GitHub Pages publishes.
PAGES_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PAGES_DIR / "lists"

session = requests.Session()
ids_by_file = {
    "series.txt": [],
    "movies.txt": [],
}


def fetch_catalog(kind, catalog_id):
    """Fetch IMDb IDs from one catalog, following its skip pagination."""
    imdb_ids = []
    skip = 0
    catalog_total = 0

    while True:
        url = (
            f"{BASE_URL.rstrip('/')}/catalog/{kind}/{catalog_id}.json"
            f"?skip={skip}"
        )

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

            if (
                isinstance(item_id, str)
                and item_id.startswith("tt")
                and item_id[2:].isdigit()
            ):
                imdb_ids.append(item_id)

        catalog_total += len(metas)
        skip += len(metas)
        print(f"{kind}: fetched {catalog_total} items", end="\r")

    return imdb_ids


for catalog in CATALOGS:
    kind = catalog["kind"]
    catalog_id = catalog["catalog_id"]

    if kind == "series":
        output_filename = "series.txt"
    elif kind in ("movie", "movies"):
        output_filename = "movies.txt"
    else:
        print(f"\nSkipping unsupported catalog kind: {kind}")
        continue

    ids_by_file[output_filename].extend(fetch_catalog(kind, catalog_id))


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for filename, ids in ids_by_file.items():
    # Remove duplicates while keeping the original order.
    unique_ids = list(dict.fromkeys(ids))
    output_path = OUTPUT_DIR / filename

    with output_path.open("w", encoding="utf-8") as file:
        if unique_ids:
            file.write("\n".join(unique_ids) + "\n")

    print(f"\nSaved {len(unique_ids)} IMDb IDs to {output_path}")

session.close()
