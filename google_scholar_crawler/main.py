from scholarly import scholarly
import json
import os
from datetime import datetime
from itertools import islice

SCHOLAR_ID = os.environ["GOOGLE_SCHOLAR_ID"]

SKIP_EDGES = os.getenv("SKIP_EDGES", "1") == "1"
MAX_PAPERS = int(os.getenv("MAX_PAPERS", "80"))
MAX_CITING_PER_PAPER = int(os.getenv("MAX_CITING_PER_PAPER", "20"))

def pub_row(p):
    b = p.get("bib", {})
    return {
        "author_pub_id": p.get("author_pub_id", ""),
        "title": b.get("title", ""),
        "year": b.get("pub_year") or b.get("year", ""),
        "venue": b.get("venue", ""),
        "num_citations": p.get("num_citations", 0),
        "pub_url": p.get("pub_url", ""),
    }

author = scholarly.search_author_id(SCHOLAR_ID)
author = scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])

papers = []
edges = []

pubs = author.get("publications", [])[:MAX_PAPERS]
for stub in pubs:
    try:
        p = scholarly.fill(stub)
    except Exception:
        continue

    pr = pub_row(p)
    papers.append(pr)

    if SKIP_EDGES or pr["num_citations"] <= 0:
        continue

    try:
        for c in islice(scholarly.citedby(p), MAX_CITING_PER_PAPER):
            cb = c.get("bib", {})
            edges.append({
                "cited_paper": pr["title"],
                "citing_paper": cb.get("title", ""),
                "citer_authors": cb.get("author", ""),
                "citing_year": cb.get("pub_year") or cb.get("year", ""),
                "citing_venue": cb.get("venue", ""),
                "citing_pub_url": c.get("pub_url", ""),
            })
    except Exception:
        pass

os.makedirs("results", exist_ok=True)

with open("results/gs_data.json", "w", encoding="utf-8") as f:
    json.dump({
        "scholar_id": SCHOLAR_ID,
        "updated": str(datetime.now()),
        "name": author.get("name", ""),
        "affiliation": author.get("affiliation", ""),
        "citedby": author.get("citedby", 0),
        "paper_count_fetched": len(papers),
        "skip_edges": SKIP_EDGES,
        "max_papers": MAX_PAPERS,
        "max_citing_per_paper": MAX_CITING_PER_PAPER,
        "papers": papers,
    }, f, ensure_ascii=False, indent=2)

with open("results/citation_edges.json", "w", encoding="utf-8") as f:
    json.dump({
        "updated": str(datetime.now()),
        "skip_edges": SKIP_EDGES,
        "edge_count": len(edges),
        "edges": edges,
    }, f, ensure_ascii=False, indent=2)

shieldio_data = {
    "schemaVersion": 1,
    "label": "citations",
    "message": f"{author.get('citedby', 0)}",
}
with open("results/gs_data_shieldsio.json", "w", encoding="utf-8") as f:
    json.dump(shieldio_data, f, ensure_ascii=False)
