import os
from typing import List, Tuple

from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# Define bot personas
BOT_PERSONAS = {
    "bot_a": "I believe AI and crypto will solve all human problems. I am highly optimistic about technology, Elon Musk, and space exploration. I dismiss regulatory concerns.",
    "bot_b": "I believe late-stage capitalism and tech monopolies are destroying society. I am highly critical of AI, social media, and billionaires. I value privacy and nature.",
    "bot_c": "I strictly care about markets, interest rates, trading algorithms, and making money. I speak in finance jargon and view everything through the lens of ROI."
}

# Load embedding model (lightweight)
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def _embed(text: str) -> np.ndarray:
    """Return a normalized embedding vector for given text."""
    vec = model.encode([text], normalize_embeddings=True)[0]
    return np.asarray(vec, dtype="float32")

class PersonaRouter:
    def __init__(self):
        self.dimension = model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)  # inner product = cosine when vectors are normalized
        self.id_to_bot = []  # list of bot ids matching index order
        self._populate_index()

    def _populate_index(self):
        embeddings = []
        for bot_id, persona in BOT_PERSONAS.items():
            emb = _embed(persona)
            embeddings.append(emb)
            self.id_to_bot.append(bot_id)
        vectors = np.stack(embeddings)
        self.index.add(vectors)

    def route_post_to_bots(self, post_content: str, threshold: float = 0.85) -> List[str]:
        """Return bot ids whose persona similarity exceeds threshold.

        Args:
            post_content: The new post text.
            threshold: Cosine similarity cutoff.
        """
        query_vec = _embed(post_content).reshape(1, -1)
        # Perform inner product search for all vectors
        scores, idxs = self.index.search(query_vec, k=len(self.id_to_bot))
        matches: List[str] = []
        for score, idx in zip(scores[0], idxs[0]):
            if score >= threshold:
                matches.append(self.id_to_bot[idx])
        return matches

# Convenience function for external callers
def route_post_to_bots(post_content: str, threshold: float = 0.85) -> List[str]:
    router = PersonaRouter()
    return router.route_post_to_bots(post_content, threshold)
