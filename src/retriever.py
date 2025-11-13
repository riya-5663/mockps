from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class TfidfRetriever:
    def __init__(self, sentences):
        self.sents = sentences
        self.corpus = [s["text"] for s in sentences]
        if len(self.corpus) == 0:
            self.vec = None
            self.mat = None
        else:
            self.vec = TfidfVectorizer(ngram_range=(1,2), max_features=5000).fit(self.corpus)
            self.mat = self.vec.transform(self.corpus)
    def retrieve(self, query, topk=5):
        if self.vec is None:
            return []
        qv = self.vec.transform([query])
        scores = (self.mat @ qv.T).toarray().ravel()
        idxs = list(np.argsort(-scores)[:topk])
        return [(self.sents[i], float(scores[i])) for i in idxs if scores[i] > 0]
