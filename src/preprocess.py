import re
from typing import List, Dict

def normalize_text(s: str) -> str:
    s = s.strip()
    s = re.sub(r'\s+', ' ', s)
    return s

def transcript_to_sentences(transcript: List[Dict]) -> List[Dict]:
    out = []
    sid = 0
    for t in transcript:
        text = normalize_text(t["text"])
        sents = re.split(r'(?<=[.!?])\s+', text)
        for s in sents:
            if s:
                out.append({"sent_id": sid, "turn_idx": t["turn_idx"], "speaker": t["speaker"], "time": t["time"], "text": s})
                sid += 1
    return out
