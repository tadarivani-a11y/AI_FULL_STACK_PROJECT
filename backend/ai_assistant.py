import os
import chromadb
from sentence_transformers import SentenceTransformer
import ollama

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")


class TrafficAI:

    def __init__(self):
        self.embedder = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.client = chromadb.PersistentClient(
            path=CHROMA_DIR
        )

        self.collection = self.client.get_or_create_collection(
            name="traffic_knowledge"
        )

        self.add_default_knowledge()

    def add_default_knowledge(self):

        knowledge = [
            "AI traffic management predicts traffic congestion using vehicle count, time, day and weather.",
            "Adaptive traffic signals change green signal duration according to traffic conditions.",
            "Low traffic requires shorter signal duration.",
            "Medium traffic requires moderate signal duration.",
            "High traffic requires longer green signal duration.",
            "Rain can increase traffic congestion because vehicles move more slowly.",
            "Emergency vehicles can receive priority at traffic signals.",
            "Historical traffic data helps machine learning models predict future traffic.",
            "AI can reduce traffic waiting time and improve road efficiency."
        ]

        if self.collection.count() == 0:

            embeddings = self.embedder.encode(
                knowledge
            ).tolist()

            self.collection.add(
                ids=[
                    f"traffic_{i}"
                    for i in range(len(knowledge))
                ],
                documents=knowledge,
                embeddings=embeddings
            )

    def search(self, question):

        embedding = self.embedder.encode(
            [question]
        ).tolist()

        results = self.collection.query(
            query_embeddings=embedding,
            n_results=3
        )

        return results["documents"][0]

    def ask(self, question):

        documents = self.search(question)

        context = "\n".join(documents)

        prompt = f"""
You are an AI Smart Traffic Management assistant.

Use the following information:

{context}

User Question:

{question}

Give a simple and useful answer.
"""

        try:

            response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response["message"]["content"]

        except Exception:

            return (
                "Ollama is not running. "
                "Please start Ollama and install "
                "the llama3.2 model."
            )