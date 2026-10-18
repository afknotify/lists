import requests

# Keep the API base URL from your existing script.
BASE_URL = "https://afknotify.github.io"

CATALOGS = [
    {"kind": "series", "catalog_id": "YOUR_SERIES_CATALOG_ID"},
    {"kind": "movie", "catalog_id": "YOUR_MOVIES_CATALOG_ID"},
]

session = requests.Session()
ids_by_file = {
    "series.txt": [],
    "movies.txt": [],
}

for catalog in CATALOGS:
    kind = catalog["kind"]
    catalog_id = catalog["catalog_id"]

    if kind == "series":
        output_file = "series.txt"
    elif kind in ("movie", "movies"):
        output_file = "movies.txt"
    else:
        print(f"Skipping unsupported catalog kind: {kind}")
        continue

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
                ids_by_file[output_file].append(item_id)

        catalog_total += len(metas)
        skip += len(metas)
        print(f"{kind} catalog: {catalog_total} items fetched", end="\r")

for filename, ids in ids_by_file.items():
    unique_ids = list(dict.fromkeys(ids))

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(unique_ids))
        if unique_ids:
            file.write("\n")

    print(f"Saved {len(unique_ids)} IMDb IDs to {filename}")

session.close()
