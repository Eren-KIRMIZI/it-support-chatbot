import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

class IntentClassifier:
    def __init__(self, data_path="data/intents.json"):
        self.vectorizer = TfidfVectorizer()
        self.model = LogisticRegression()
        self.train(data_path)

    def train(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts = [item["text"] for item in data]
        labels = [item["intent"] for item in data]

        X = self.vectorizer.fit_transform(texts)
        self.model.fit(X, labels)

    def predict(self, text):
        X = self.vectorizer.transform([text])
        return self.model.predict(X)[0]
