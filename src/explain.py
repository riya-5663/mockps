# src/explain.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from src.preprocess import transcript_to_sentences
from src.candidate_extractor import extract_candidates
from src.retriever import TfidfRetriever

# optional: SBERT retriever (if present)
try:
    from src.sbert_retriever import SBertRetriever
    _HAS_SBERT = True
except Exception:
    SBertRetriever = None
    _HAS_SBERT = False

def load_model(model_dir):
    tok = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    model.eval()
    return tok, model

def score_pair(tokenizer, model, query, candidate_text, device=None):
    if device is None:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    inputs = tokenizer(query, candidate_text, return_tensors="pt", truncation=True, padding=True, max_length=256).to(device)
    model = model.to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
    return float(probs[1])

def _build_candidates(sents, query, topk=10):
    """
    Return list of candidate sentence dicts (with sent metadata) for scoring.
    Try high-precision pattern extraction first, otherwise use semantic/Tf-idf retrieval.
    """
    candidates = extract_candidates(sents)
    if candidates:
        # remove duplicates if any
        seen = set()
        uniq = []
        for c in candidates:
            t = c["text"].strip()
            if t not in seen:
                uniq.append(c)
                seen.add(t)
        return uniq

    # use SBERT if available, else TF-IDF
    if _HAS_SBERT:
        try:
            retr = SBertRetriever()
            retr.build(sents)
            items = retr.retrieve(query, topk=topk)
            return [it[0] for it in items]
        except Exception:
            pass

    # fallback TF-IDF
    retr = TfidfRetriever(sents)
    items = retr.retrieve(query, topk=topk)
    return [it[0] for it in items]

def _synthesize_explanation(query, scored, max_sentences=2):
    """
    Produce a concise natural-language explanation string from the
    ranked scored candidates list (each item has candidate, score, context).
    Strategy:
      - take top candidate (highest score) as main cause
      - optionally include 1-2 supporting phrases from other high-ranked items
      - include a cautious hedging phrase with score when not confident
    """
    if not scored:
        return "No clear explanation could be found in the transcript."

    # top item
    top = scored[0]
    top_text = top["candidate"]["text"].strip()
    top_score = top["score"]

    # gather additional supportive short texts (avoid duplicates)
    support_texts = []
    seen = {top_text}
    for item in scored[1: max_sentences+2]:
        t = item["candidate"]["text"].strip()
        if t not in seen:
            support_texts.append(t)
            seen.add(t)
        if len(support_texts) >= (max_sentences - 1):
            break

    # craft explanation
    if top_score >= 0.75:
        hedge = "The most likely reason"
    elif top_score >= 0.45:
        hedge = "A likely reason"
    else:
        hedge = "A possible reason"

    explanation = f"{hedge} is: \"{top_text}\" (confidence {top_score:.2f})."
    if support_texts:
        explanation += " Additional supporting points: " + "; ".join(f"\"{s}\"" for s in support_texts) + "."
    return explanation

def explain(transcript, query, tokenizer, model, top_k=3):
    """
    Main entry point.
    - transcript: list of turn dicts with keys (turn_idx, speaker, time, text)
    - query: string
    - tokenizer, model: pairwise classifier
    Returns a dictionary:
      {
        "query": query,
        "explanation": "...",          # natural-language answer summary
        "claims": [                    # ranked claims with score + evidence list
           {
             "claim_text": "...",
             "score": 0.87,
             "evidence": [ {sent metadata}, ... ]
           },...
        ]
      }
    """
    # 1) split transcript into sentence-level items
    sents = transcript_to_sentences(transcript)

    # 2) obtain candidate sentences
    candidates = _build_candidates(sents, query, topk=20)

    # 3) score candidates
    scored = []
    for c in candidates:
        cand_text = c["text"]
        try:
            score = score_pair(tokenizer, model, query, cand_text)
        except Exception:
            score = 0.0
        # context window: ±2 sentences (by sent_id)
        context = [x for x in sents if abs(x["sent_id"] - c["sent_id"]) <= 2]
        scored.append({"candidate": c, "score": score, "context": context})

    # 4) sort descending by score
    scored = sorted(scored, key=lambda x: -x["score"])

    # 5) synthesize a short natural-language explanation
    explanation_text = _synthesize_explanation(query, scored, max_sentences=2)

    # 6) format claims: include claim_text, numeric score and evidence list
    claims = []
    for item in scored[:top_k]:
        claim_text = item["candidate"]["text"].strip()
        evidence = [
            {
                "sent_id": c["sent_id"],
                "turn_idx": c["turn_idx"],
                "speaker": c["speaker"],
                "time": c["time"],
                "text": c["text"]
            }
            for c in item["context"]
        ]
        claims.append({
            "claim_text": claim_text,
            "score": item["score"],
            "evidence": evidence
        })

    return {
        "query": query,
        "explanation": explanation_text,
        "claims": claims
    }
