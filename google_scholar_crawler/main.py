from scholarly import scholarly
import json
import os
from datetime import datetime

SCHOLAR_ID = os.environ["GOOGLE_SCHOLAR_ID"]

author = scholarly.search_author_id(SCHOLAR_ID)
author = scholarly.fill(author, sections=["basics", "indices", "counts"])

result = {
  "scholar_id": SCHOLAR_ID,
  "updated": str(datetime.now()),
  "name": author.get("name", ""),
  "affiliation": author.get("affiliation", ""),
  "citedby": author.get("citedby", 0),
  "hindex": author.get("hindex", 0),
  "i10index": author.get("i10index", 0),
}
os.makedirs("results", exist_ok=True)

with open("results/gs_data.json", "w", encoding="utf-8") as f:
  json.dump(result, f, ensure_ascii=False, indent=2)

with open("results/citation_edges.json", "w", encoding="utf-8") as f:
  json.dump({"updated": str(datetime.now()), "edge_count": 0, "edges": []}, f, ensure_ascii=False, indent=2)

with open("results/gs_data_shieldsio.json", "w", encoding="utf-8") as f:
  json.dump({"schemaVersion": 1, "label": "citations", "message": str(result["citedby"])}, f, ensure_ascii=False)
