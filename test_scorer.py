from scorer import score_answer, normalize

def test_exact_match():
    score, reason = score_answer("Earth", "Earth")
    assert score == 1.0
    assert "Exact match" in reason
    print(f"✅ test_exact_match passed: score={score}")

def test_case_insensitive_exact_match():
    score, reason = score_answer("approved", "Approved")
    assert score == 1.0
    assert "Exact match" in reason
    print(f"✅ test_case_insensitive passed: score={score}")

def test_partial_match():
    score, reason = score_answer("4", "The answer is 4.")
    assert 0.0 < score < 1.0
    print(f"✅ test_partial_match passed: score={score}, reason={reason}")

def test_wrong_answer():
    score, reason = score_answer("red", "blue")
    assert score == 0.0
    print(f"✅ test_wrong_answer passed: score={score}")

def test_missing_model_answer():
    score, reason = score_answer("Earth", "")
    assert score == 0.0
    assert "missing" in reason.lower()
    print(f"✅ test_missing_answer passed: score={score}")

def test_normalize():
    assert normalize("  Hello World  ") == "hello world"
    print("✅ test_normalize passed")

if __name__ == "__main__":
    test_exact_match()
    test_case_insensitive_exact_match()
    test_partial_match()
    test_wrong_answer()
    test_missing_model_answer()
    test_normalize()
    print("\n✅ All tests passed.")

    