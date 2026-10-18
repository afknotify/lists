import json
import urllib.request

SOURCES = {
    "released-series-ids.txt":
        "https://dracid-lists-addon.dracid.workers.dev/c/cmVsZWFzZWQtbW92aWVzfnJlbGVhc2VkLXNlcmllcw/catalog/movie/released-movies.json",
    "released-movie-ids.txt":
        "https://dracid-lists-addon.dracid.workers.dev/c/cmVsZWFzZWQtbW92aWVzfnJlbGVhc2VkLXNlcmllcw/catalog/series/released-series.jsonm",
}

for filename, url in SOURCES.items():
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "GitHub-Actions-ID-fetcher"},
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)

    metas = data.get("metas") if isinstance(data, dict) else None
    if not isinstance(metas, list):
        raise ValueError(f"{url} did not contain a 'metas' array")

    ids = list(dict.fromkeys(
        item["id"]
        for item in metas
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    ))

    if not ids:
        raise ValueError(
            f"No IDs found for {filename}; existing file will not be replaced"
        )

    with open(filename, "w", encoding="utf-8") as output:
        output.write("\n".join(ids) + "\n")

    print(f"Wrote {len(ids)} IDs to {filename}")
