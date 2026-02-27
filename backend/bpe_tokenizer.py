"""
Phase II - Byte Pair Encoding (BPE) Tokenizer
Trained from scratch on Urdu corpus (no pre-built tokenizer libraries)
Vocabulary size: 250
"""

import re
import json
import logging
from pathlib import Path
from collections import defaultdict

# ── Config ─────────────────────────────────────────────────────────────────────
CORPUS_FILE  = Path("corpus.txt")
MODEL_FILE   = Path("bpe_tokenizer.json")
VOCAB_SIZE   = 250

# Special tokens (same unicode bytes used in preprocessing)
SPECIAL_TOKENS = {
    "<EOS>": "\uE001",
    "<EOP>": "\uE002",
    "<EOT>": "\uE003",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ── Step 1: Build initial vocabulary from characters ──────────────────────────
def get_vocab(corpus: str) -> dict[str, int]:
    """
    Split corpus into words and represent each word as a sequence of characters
    with a special end-of-word marker </w>.
    Returns a dict of {word_as_char_tuple: frequency}
    """
    vocab = defaultdict(int)
    # Tokenize on whitespace, preserve special token characters
    for word in corpus.split():
        if not word:
            continue
        # Represent word as space-separated characters with </w> at end
        char_word = " ".join(list(word)) + " </w>"
        vocab[char_word] += 1
    return dict(vocab)


# ── Step 2: Count symbol pair frequencies ─────────────────────────────────────
def get_pair_freqs(vocab: dict[str, int]) -> dict[tuple, int]:
    """Count frequency of every adjacent symbol pair across all words."""
    pairs = defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs[(symbols[i], symbols[i + 1])] += freq
    return dict(pairs)


# ── Step 3: Merge best pair in vocabulary ─────────────────────────────────────
def merge_vocab(pair: tuple, vocab: dict[str, int]) -> dict[str, int]:
    """Merge all occurrences of the best pair into a single symbol."""
    new_vocab = {}
    # Escape special regex characters in the pair
    bigram = re.escape(" ".join(pair))
    pattern = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
    merged = "".join(pair)
    for word, freq in vocab.items():
        new_word = pattern.sub(merged, word)
        new_vocab[new_word] = freq
    return new_vocab


# ── Step 4: Build initial character-level base vocabulary ─────────────────────
def get_base_vocab(vocab: dict[str, int]) -> set[str]:
    """Extract all unique characters/symbols from initial vocab."""
    base = set()
    for word in vocab:
        for symbol in word.split():
            base.add(symbol)
    return base


# ── Step 5: BPE Training ───────────────────────────────────────────────────────
def train_bpe(corpus: str, vocab_size: int) -> dict:
    """
    Full BPE training loop.
    Returns tokenizer model: base vocab + merge rules.
    """
    log.info("Building initial character-level vocabulary...")
    vocab = get_vocab(corpus)
    base_vocab = get_base_vocab(vocab)
    log.info("Initial vocabulary size (unique chars): %d", len(base_vocab))
    log.info("Unique words in corpus: %d", len(vocab))

    # Merges we will learn
    merges = []
    merged_vocab = set(base_vocab)

    # How many merges do we need?
    # vocab_size = base_vocab_size + num_merges
    num_merges = vocab_size - len(base_vocab)
    if num_merges <= 0:
        log.warning("Base vocab (%d) already >= target vocab size (%d). No merges needed.",
                    len(base_vocab), vocab_size)
        num_merges = 0

    log.info("Target vocab size: %d | Base: %d | Merges needed: %d",
             vocab_size, len(base_vocab), num_merges)

    for i in range(num_merges):
        pair_freqs = get_pair_freqs(vocab)
        if not pair_freqs:
            log.info("No more pairs to merge at step %d.", i)
            break

        # Pick the most frequent pair
        best_pair = max(pair_freqs, key=pair_freqs.get)
        best_freq = pair_freqs[best_pair]

        if best_freq < 2:
            log.info("Best pair frequency is %d — stopping early at step %d.", best_freq, i)
            break

        # Merge it
        vocab = merge_vocab(best_pair, vocab)
        merged_symbol = "".join(best_pair)
        merges.append(best_pair)
        merged_vocab.add(merged_symbol)

        if (i + 1) % 50 == 0 or i < 5:
            log.info("  Merge %d/%d: %r + %r → %r  (freq=%d)",
                     i + 1, num_merges, best_pair[0], best_pair[1], merged_symbol, best_freq)

    log.info("Training complete. Final vocab size: %d", len(merged_vocab))
    return {
        "vocab":  sorted(merged_vocab),
        "merges": [list(m) for m in merges],
        "special_tokens": SPECIAL_TOKENS,
        "vocab_size": len(merged_vocab),
    }


# ── Tokenizer class (for inference/use in Phase III) ──────────────────────────
class BPETokenizer:
    def __init__(self, model_path: str = str(MODEL_FILE)):
        data = json.loads(Path(model_path).read_text(encoding="utf-8"))
        self.vocab   = data["vocab"]
        self.merges  = [tuple(m) for m in data["merges"]]
        self.special = data["special_tokens"]
        # Token → ID and ID → Token mappings
        self.token2id = {tok: i for i, tok in enumerate(self.vocab)}
        self.id2token = {i: tok for i, tok in enumerate(self.vocab)}

    def _tokenize_word(self, word: str) -> list[str]:
        """Apply learned BPE merges to a single word."""
        symbols = list(word) + ["</w>"]

        for pair in self.merges:
            i = 0
            new_symbols = []
            while i < len(symbols):
                if i < len(symbols) - 1 and (symbols[i], symbols[i+1]) == pair:
                    new_symbols.append(symbols[i] + symbols[i+1])
                    i += 2
                else:
                    new_symbols.append(symbols[i])
                    i += 1
            symbols = new_symbols

        return symbols

    def encode(self, text: str) -> list[int]:
        """Encode a string into token IDs."""
        tokens = []
        for word in text.split():
            word_tokens = self._tokenize_word(word)
            for t in word_tokens:
                tokens.append(self.token2id.get(t, self.token2id.get("</w>", 0)))
        return tokens

    def decode(self, ids: list[int]) -> str:
        """Decode token IDs back to string."""
        tokens = [self.id2token.get(i, "") for i in ids]
        text = "".join(tokens)
        text = text.replace("</w>", " ")
        return text.strip()

    def tokenize(self, text: str) -> list[str]:
        """Return list of token strings (not IDs)."""
        tokens = []
        for word in text.split():
            tokens.extend(self._tokenize_word(word))
        return tokens


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    if not CORPUS_FILE.exists():
        log.error("corpus.txt not found! Run preprocess.py first.")
        return

    log.info("Loading corpus from %s ...", CORPUS_FILE)
    corpus = CORPUS_FILE.read_text(encoding="utf-8")
    log.info("Corpus size: %d characters", len(corpus))

    # Train
    model = train_bpe(corpus, VOCAB_SIZE)

    # Save model
    MODEL_FILE.write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info("Tokenizer model saved → %s", MODEL_FILE)

    # ── Quick sanity check ─────────────────────────────────────────────────────
    log.info("\n── Sanity Check ──")
    tokenizer = BPETokenizer()

    sample = "بہلول مجذوب ہارون الرشید کے زمانے میں ایک بزرگ تھے۔"
    tokens  = tokenizer.tokenize(sample)
    ids     = tokenizer.encode(sample)
    decoded = tokenizer.decode(ids)

    log.info("Sample text : %s", sample)
    log.info("Tokens      : %s", tokens)
    log.info("Token IDs   : %s", ids)
    log.info("Decoded     : %s", decoded)
    log.info("Vocab size  : %d", len(tokenizer.vocab))
    log.info("Merge rules : %d", len(tokenizer.merges))


if __name__ == "__main__":
    main()