import json
import re
from urllib.request import Request, urlopen

SOURCE_API = (
    "https://api.github.com/repos/dracid77/lists/contents/"
    "addon/catalog/movie/released-movies"
)
OUTPUT_FILE = "imdb_ids.txt"
IMDB_ID_PATTERN = re.compile(r"tt\d+")


def fetch_json(url):
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "imdb-id-exporter",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def find_ids(value):
    """Yield IMDb ID-shaped strings in JSON traversal order."""
    if isinstance(value, str):
        yield from IMDB_ID_PATTERN.findall(value)
    elif isinstance(value, list):
        for item in value:
            yield from find_ids(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from find_ids(item)


def main():
    entries = fetch_json(SOURCE_API)
    json_files = sorted(
        (
            entry
            for entry in entries
            if entry.get("type") == "file"
            and entry.get("name", "").lower().endswith(".json")
            and entry.get("download_url")
        ),
        key=lambda entry: entry["name"],
    )

    if not json_files:
        raise RuntimeError("No JSON files found in the source directory.")

    ids = []
    for entry in json_files:
        data = fetch_json(entry["download_url"])
        ids.extend(find_ids(data))

    if not ids:
        raise RuntimeError("No IMDb IDs found; leaving the existing output untouched.")

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as output:
        output.write("\n".join(ids) + "\n")

    print(f"Wrote {len(ids)} IMDb IDs from {len(json_files)} JSON files.")


if __name__ == "__main__":
    main()
