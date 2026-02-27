# updated model.py
import os
import pickle
import random
from collections import Counter

# -------------------------
# 1️⃣ Load model.pkl
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

with open(MODEL_PATH, "rb") as f:
    model_data = pickle.load(f)

unigrams = model_data["unigrams"]
bigrams = model_data["bigrams"]
trigrams = model_data["trigrams"]
total_tokens = model_data["total_tokens"]

# -------------------------
# 2️⃣ Interpolation weights
# -------------------------
lambda1 = 0.2
lambda2 = 0.3
lambda3 = 0.5

# -------------------------
# 3️⃣ Interpolated trigram probability
# -------------------------
def interpolated_prob(w1, w2, w3):
    tri_count = trigrams.get((w1, w2, w3), 0)
    bi_count = bigrams.get((w1, w2), 0)
    bi_count2 = bigrams.get((w2, w3), 0)
    uni_count = unigrams.get(w3, 0)
    
    p_tri = tri_count / bi_count if bi_count > 0 else 0
    p_bi = bi_count2 / unigrams[w2] if unigrams[w2] > 0 else 0
    p_uni = uni_count / total_tokens
    
    return lambda3*p_tri + lambda2*p_bi + lambda1*p_uni

# -------------------------
# 4️⃣ Generate one sentence
# -------------------------
def generate_sentence(max_words=50):
    sentence = ["<BOS>", "<BOS>"]
    
    for _ in range(max_words):
        w1, w2 = sentence[-2], sentence[-1]
        candidates = list(unigrams.keys())
        probs = [interpolated_prob(w1, w2, w3) for w3 in candidates]
        total = sum(probs)
        if total == 0:
            break
        probs = [p/total for p in probs]
        next_word = random.choices(candidates, probs)[0]
        sentence.append(next_word)
        if next_word == "<EOT>":
            break
    
    return [w for w in sentence if w not in ["<BOS>", "<EOT>"]]

# -------------------------
# 5️⃣ Generate full story
# -------------------------
def generate_story(prefix="", max_sentences=5):
    story = []
    
    # Add prefix if provided
    if prefix.strip():
        story.append(prefix)
    
    for _ in range(max_sentences):
        words = generate_sentence()
        if words:
            story.append(" ".join(words) + "۔")  # Urdu full stop
    
    return " ".join(story)