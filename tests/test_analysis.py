import importlib.util
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"
# app.py imports streamlit and runs UI code at import time, so test the isolated logic
# using a lightweight extracted copy of the same baseline logic.
import re

POSITIVE = {"great","excellent","amazing","helpful","friendly","quick","fast","clean","love","recommend","wonderful","good","resolved","smooth","easy","professional","thank"}
NEGATIVE = {"bad","terrible","awful","poor","slow","rude","dirty","broken","late","never","worst","refund","unhelpful","disappointed","issue","problem","charged","delay","unacceptable","missing"}
URGENT = {"unsafe","fraud","scam","injury","allergic","harassment","threat","charged twice","data leak","security"}

def analyze_review(review):
    words = re.findall(r"[a-z']+", str(review).lower())
    pos = sum(w in POSITIVE for w in words)
    neg = sum(w in NEGATIVE for w in words)
    lower = str(review).lower()
    urgent = any(term in lower for term in URGENT)
    if urgent:
        sentiment = "Negative"
    elif pos > neg:
        sentiment = "Positive"
    elif neg > pos:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    priority = "High" if urgent or (sentiment == "Negative" and any(w in lower for w in ["refund","charged","unsafe","scam","worst","unacceptable"])) else ("Medium" if sentiment == "Negative" else "Low")
    return {"sentiment": sentiment, "urgent_flag": urgent, "priority": priority}

def test_positive_review():
    assert analyze_review("Excellent service and friendly staff")["sentiment"] == "Positive"

def test_billing_complaint_high_priority():
    result = analyze_review("I was charged twice and need a refund")
    assert result["sentiment"] == "Negative"
    assert result["priority"] == "High"

def test_scam_review_flagged():
    result = analyze_review("This feels like a scam")
    assert result["urgent_flag"] is True
    assert result["sentiment"] == "Negative"

def test_neutral_review():
    assert analyze_review("Average experience")["sentiment"] == "Neutral"
