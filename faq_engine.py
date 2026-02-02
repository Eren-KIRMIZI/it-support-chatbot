import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class FAQEngine:
    def __init__(self, faq_path="data/faq.json"):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.faq = self.load_faq(faq_path)
        self.embeddings = self.embed_questions()

    def load_faq(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def embed_questions(self):
        questions = [item["question"] for item in self.faq]
        return self.model.encode(questions)

    def search(self, query, threshold=0.75):
        query_vec = self.model.encode([query])
        scores = cosine_similarity(query_vec, self.embeddings)[0]
        best_idx = np.argmax(scores)

        if scores[best_idx] >= threshold:
            return self.faq[best_idx]["answer"]

        return None
