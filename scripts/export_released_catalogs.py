import json
import sys
from pathlib import Path

TITLE_KEYS = ("title", "name")
DATE_KEYS = (
    "release_date",
    "releasedate",
    "releaseinfo",
    "released",
    "premiered",
    "date",
    "year",
)


def find_value(record, keys):
    normalized = {str(key).lower(): value for key, value in record.items()}

    for key in keys:
        value = normalized.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()

    return None


def records_in(value):
    """Yield title/date records in the order they appear in the JSON."""
    if isinstance(value, list):
        for item in value:
            yield from records_in(item)
    elif isinstance(value, dict):
        title = find_value(value, TITLE_KEYS)
        date = find_value(value, DATE_KEYS)

        if title and date:
            yield title, date
            return

        for child in value.values():
            yield from records_in(child)


def export_folder(source_dir, output_file):
    source_dir = Path(source_dir)
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    lines = []

    # Sorting filenames makes the order across separate files deterministic.
    # Records within each JSON file are emitted in their original order.
    json_files = sorted(source_dir.rglob("*.json"))
    for json_file in json_files:
        with json_file.open(encoding="utf-8") as file:
            data = json.load(file)

        lines.extend(f'{title} "{date}"' for title, date in records_in(data))

    if not lines:
        raise ValueError(f"No title/date records found in {source_dir}")

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} entries to {output_file}")


def main():
    if len(sys.argv) != 4:
        raise SystemExit(
            "Usage: export_released_catalogs.py MOVIES_DIR SERIES_DIR OUTPUT_DIR"
        )

    movies_dir, series_dir, output_dir = sys.argv[1:]
    output_dir = Path(output_dir)

    export_folder(movies_dir, output_dir / "released-movies.txt")
    export_folder(series_dir, output_dir / "released-series.txt")


if __name__ == "__main__":
    main()
