import json
import sys
from pathlib import Path


def ids_in(value):
    """Yield entry IDs in the order they appear in the JSON."""
    if isinstance(value, list):
        for item in value:
            yield from ids_in(item)

    elif isinstance(value, dict):
        normalized = {str(key).lower(): item for key, item in value.items()}
        entry_id = normalized.get("id")

        if entry_id is not None and str(entry_id).strip():
            yield str(entry_id).strip()
            return

        for child in value.values():
            yield from ids_in(child)


def export_folder(source_dir, primary_filename, output_file):
    source_dir = Path(source_dir)
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    # Check for the priority file inside the source directory or beside it.
    primary_candidates = (
        source_dir / primary_filename,
        source_dir.parent / primary_filename,
    )
    primary_json = next(
        (path for path in primary_candidates if path.is_file()),
        None,
    )
    if primary_json is None:
        raise FileNotFoundError(
            f"Priority JSON file not found. Checked: "
            f"{', '.join(str(path) for path in primary_candidates)}"
        )

    # Process the priority file first, then the remaining JSON files.
    json_files = [primary_json]
    json_files.extend(
        path
        for path in sorted(source_dir.rglob("*.json"))
        if path.resolve() != primary_json.resolve()
    )

    lines = []
    for json_file in json_files:
        with json_file.open(encoding="utf-8") as file:
            data = json.load(file)

        lines.extend(ids_in(data))

    if not lines:
        raise ValueError(f"No entry IDs found in {source_dir}")

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

    export_folder(
        movies_dir,
        "released-movies.json",
        output_dir / "released-movies.txt",
    )
    export_folder(
        series_dir,
        "released-series.json",
        output_dir / "released-series.txt",
    )


if __name__ == "__main__":
    main()
