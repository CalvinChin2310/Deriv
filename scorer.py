import re
from typing import Tuple

def normalize(text: str) -> str:
    """Lowercase and strip whitespace."""
    return text.lower().strip()

def tokenize(text: str) -> set:
    """Split normalized text into tokens, stripping punctuation."""
    return set(re.findall(r'\b\w+\b', text))

def score_answer(reference: str, model: str) -> Tuple[float, str]:
    """
    Score a model answer against a reference answer.
    
    Returns:
        (score, reason) tuple
        score: 0.0 to 1.0
        reason: human-readable explanation
    """
    # Edge case: missing or empty answers
    if not reference or not reference.strip():
        return 0.0, "Reference answer is missing or empty"
    if not model or not model.strip():
        return 0.0, "Model answer is missing or empty"

    norm_ref = normalize(reference)
    norm_model = normalize(model)

    # Exact match after normalization
    if norm_ref == norm_model:
        return 1.0, "Exact match after normalization"

    # Token overlap scoring
    ref_tokens = tokenize(norm_ref)
    model_tokens = tokenize(norm_model)

    # How many reference tokens appear in the model answer
    matched = ref_tokens & model_tokens
    
    if not ref_tokens:
        return 0.0, "Reference answer has no tokens to match"
    
    # Score = proportion of reference tokens found in model answer
    # This rewards model answers that contain the full reference (e.g. "The answer is 4" contains "4")
    containment_score = len(matched) / len(ref_tokens)

    # Also compute Jaccard for balance (penalizes overly verbose answers slightly)
    union = ref_tokens | model_tokens
    jaccard_score = len(matched) / len(union)

    # Weighted blend: favour containment (captures "answer is 4" case well)
    final_score = round(0.7 * containment_score + 0.3 * jaccard_score, 4)

    reason = (
        f"Partial match — {len(matched)}/{len(ref_tokens)} reference tokens found. "
        f"Containment: {containment_score:.2f}, Jaccard: {jaccard_score:.2f}"
    )

    return final_score, reason