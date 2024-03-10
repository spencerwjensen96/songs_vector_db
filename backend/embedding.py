import numpy as np

def generate_embedding(input_string: str) -> np.ndarray:
    embedding = np.random.default_rng().random((1,100))
    return embedding
