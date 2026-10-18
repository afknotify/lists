    while True:
        # Use a query parameter (?skip=) instead of a path segment (/skip=)
        url = f"{BASE_URL}/catalog/{kind}/{catalog_id}.json?skip={skip}"
        
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
            if item_id.startswith("tt") and item_id[2:].isdigit():
                data_by_kind[kind].append({
                    "id": item_id,
                    "title": meta.get("name", item_id)
                })

        catalog_total += len(metas)
        skip += len(metas)
        print(f"({catalog_total} items...)", end=" ")
        
