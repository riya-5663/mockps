# src/sbert_retriever.py
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

class SBertRetriever:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.embeddings = None
        self.sents = None

    def build(self, sentences):
        # sentences: list of dicts with 'text'
        self.sents = sentences
        texts = [s["text"] for s in sentences]
        emb = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        self.embeddings = emb.astype("float32")
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)   # cosine via normalized vectors
        self.index.add(self.embeddings)

    def retrieve(self, query, topk=5):
        q_emb = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype("float32")
        D, I = self.index.search(q_emb, topk)
        res = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0: continue
            res.append((self.sents[int(idx)], float(score)))
        return res
