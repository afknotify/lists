def export_folder(source_dir, output_file):
    source_dir = Path(source_dir)
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    # For example, released-movies/ uses the sibling released-movies.json first.
    primary_json = source_dir.parent / f"{source_dir.name}.json"
    if not primary_json.is_file():
        raise FileNotFoundError(f"Priority JSON file not found: {primary_json}")

    json_files = [primary_json]
    json_files.extend(
        path
        for path in sorted(source_dir.rglob("*.json"))
        if path != primary_json
    )

    lines = []
    for json_file in json_files:
        with json_file.open(encoding="utf-8") as file:
            data = json.load(file)

        # Preserve item order within each JSON file.
        lines.extend(f"{title} ({date})" for title, date in records_in(data))

    if not lines:
        raise ValueError(f"No title/date records found in {source_dir}")

    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(lines)} entries to {output_file}")
