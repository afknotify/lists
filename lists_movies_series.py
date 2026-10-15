import requests

base = (
    "https://dracid-lists-addon.dracid.workers.dev"
    "/c/cmVsZWFzZWQtbW92aWVzfnJlbGVhc2VkLXNlcmllcw"
)

session = requests.Session()
manifest = session.get(f"{base}/manifest.json", timeout=30).json()

ids_by_kind = {
    "movie": set(),
    "series": set(),
}

for catalog in manifest.get("catalogs", []):
    kind = catalog["type"]

    # Ignore catalog types other than movies and series.
    if kind not in ids_by_kind:
        continue

    catalog_id = catalog["id"]
    skip = 0

    while True:
        suffix = "" if skip == 0 else f"/skip={skip}"
        url = f"{base}/catalog/{kind}/{catalog_id}{suffix}.json"
        response = session.get(url, timeout=30)
        response.raise_for_status()
        metas = response.json().get("metas", [])

        if not metas:
            break

        for meta in metas:
            item_id = meta.get("id", "")
            if item_id.startswith("tt") and item_id[2:].isdigit():
                ids_by_kind[kind].add(item_id)

        skip += len(metas)

for kind, filename in [
    ("movie", "movies_imdb_ids.txt"),
    ("series", "series_imdb_ids.txt"),
]:
    ids = sorted(ids_by_kind[kind])
    with open(filename, "w") as f:
        f.write("\n".join(ids) + ("\n" if ids else ""))
    print(f"Saved {len(ids)} {kind} IMDb IDs to {filename}")
