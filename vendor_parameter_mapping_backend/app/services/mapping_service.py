import re
from typing import List, Dict, Any
from ..db import get_collections

def _tokenize(s: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9]+", (s or "").lower())

def _jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / float(len(sa | sb))

# PUBLIC_INTERFACE
def suggest_standard_keys(vendor_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Suggest standard parameter keys for a vendor based on a query string.

    Strategy:
      - Prefer existing mappings for the vendor with text index by regex search on vendor_parameter_name and standard_parameter_key.
      - Use simple token overlap scoring as fallback.

    Returns:
        List of suggestion dicts with fields: standard_parameter_key, confidence, vendor_parameter_name
    """
    cols = get_collections()
    mappings = cols["mappings"]

    token_q = _tokenize(query)

    # Primary: search existing mappings for this vendor
    regex = re.compile(re.escape(query), re.IGNORECASE)
    cursor = mappings.find(
        {
            "vendor_id": vendor_id,
            "$or": [
                {"vendor_parameter_name": {"$regex": regex}},
                {"standard_parameter_key": {"$regex": regex}},
            ],
        }
    )
    scored = []
    for m in cursor:
        # score by jaccard between query and vendor parameter name
        vname = m.get("vendor_parameter_name", "")
        score = max(_jaccard(token_q, _tokenize(vname)), float(m.get("confidence", 0)))
        scored.append(
            {
                "standard_parameter_key": m["standard_parameter_key"],
                "confidence": round(min(1.0, score), 4),
                "vendor_parameter_name": vname,
            }
        )

    # If not enough, try vendor_parameters names
    if len(scored) < limit:
        vp_cursor = cols["vendor_parameters"].find({"vendor_id": vendor_id, "name": {"$regex": regex}})
        for vp in vp_cursor:
            # weak suggestion without mapping, low confidence
            scored.append(
                {
                    "standard_parameter_key": "",
                    "confidence": 0.3,
                    "vendor_parameter_name": vp.get("name", ""),
                }
            )

    # Deduplicate by key/name pair keeping highest confidence
    uniq = {}
    for s in scored:
        key = (s["standard_parameter_key"], s["vendor_parameter_name"])
        if key not in uniq or s["confidence"] > uniq[key]["confidence"]:
            uniq[key] = s
    result = list(uniq.values())
    result.sort(key=lambda x: x["confidence"], reverse=True)
    return result[:limit]
