import re
from typing import List, Dict

PATTERNS = {
    # Original patterns
    "unconfirmed_resource": [r"not .*confirmed", r"haven'?t .*confirmed", r"no .*license", r"no .*access", r"haven't got license"],
    "ownership_confusion": [r"who (is|was) (responsible|own|owns|taking)", r"who else", r"who owns"],
    "defer_decision": [r"decide (later|next week|tomorrow)", r"let's decide", r"table this", r"we should wait"],
    "conflict": [r"disagree", r"can't do", r"not possible", r"we can't"],
    
    # NEW PATTERNS for financial and failure-to-act causality
    "financial_issue": [r"(over|under) budget", r"price hike", r"cost increase", r"price increase", r"\$"],
    "missed_action": [r"didn'?t confirm", r"failed to", r"missed the deadline", r"not finalized", r"not paid", r"no confirmation"],
    "direct_causality": [r"(due to|because of|led to|caused)"],
}

def extract_candidates(sentences: List[Dict]) -> List[Dict]:
    candidates = []
    for s in sentences:
        txt = s["text"].lower()
        for label, patterns in PATTERNS.items():
            for p in patterns:
                if re.search(p, txt):
                    cand = dict(s)
                    cand["pattern_label"] = label
                    candidates.append(cand)
                    break
    return candidates