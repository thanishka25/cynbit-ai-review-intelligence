import re
import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Revio AI Review Intelligence", page_icon="⭐", layout="wide")

POSITIVE = {"great","excellent","amazing","helpful","friendly","quick","fast","clean","love","recommend","wonderful","good","resolved","smooth","easy","professional","thank"}
NEGATIVE = {"bad","terrible","awful","poor","slow","rude","dirty","broken","late","never","worst","refund","unhelpful","disappointed","issue","problem","charged","delay","unacceptable","missing"}
URGENT = {"unsafe","fraud","scam","injury","allergic","harassment","threat","charged twice","data leak","security"}

def tokenize(text):
    return re.findall(r"[a-z']+", str(text).lower())

def analyze_review(review):
    words = tokenize(review)
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
    themes = []
    theme_map = {
        "Service": ["staff", "service", "support", "rude", "helpful", "friendly"],
        "Delivery / Timeliness": ["late", "delivery", "slow", "delay", "quick", "fast"],
        "Product / Quality": ["quality", "broken", "clean", "dirty", "product", "room"],
        "Billing": ["charged", "refund", "payment", "bill", "price"],
        "Resolution": ["resolved", "response", "issue", "problem", "fixed"]
    }
    for theme, terms in theme_map.items():
        if any(t in lower for t in terms):
            themes.append(theme)
    priority = "High" if urgent or (sentiment == "Negative" and any(w in lower for w in ["refund","charged","unsafe","scam","worst","unacceptable"])) else ("Medium" if sentiment == "Negative" else "Low")
    return {"sentiment": sentiment, "positive_hits": pos, "negative_hits": neg,
            "urgent_flag": urgent, "priority": priority, "themes": ", ".join(themes) or "General feedback"}

def draft_response(review, sentiment, business_name):
    if sentiment == "Positive":
        return f"Thank you for sharing your experience with {business_name}. We're glad to hear it went well, and we appreciate your support."
    if sentiment == "Negative":
        return f"Thank you for bringing this to our attention. We're sorry your experience did not meet expectations. We'd like to understand what happened and help resolve it. Please contact our team directly with the relevant details."
    return f"Thank you for your feedback about {business_name}. We appreciate you taking the time to share it and will use it to improve our service."

st.title("⭐ Revio AI Review Intelligence")
st.caption("Assessment proof of concept • Review triage, sentiment signals, theme detection, and draft replies")
st.info("Prototype notice: this demo uses a transparent keyword baseline and synthetic/sample reviews. It is not connected to Cynbit or any live review platform. Human approval is required before publishing replies.")

with st.sidebar:
    st.header("Settings")
    business_name = st.text_input("Business name", "Sample Business")
    st.write("Upload a CSV with a column named `review`, or use the sample dataset.")
    uploaded = st.file_uploader("Review CSV", type=["csv"])

default_reviews = [
    {"review_id": "R001", "location": "Jaipur Central", "rating": 5, "review": "Friendly staff and quick service. Great experience, highly recommend."},
    {"review_id": "R002", "location": "Jaipur Central", "rating": 1, "review": "I was charged twice and support was slow. I need a refund."},
    {"review_id": "R003", "location": "North Branch", "rating": 3, "review": "The product is fine but delivery was late."},
    {"review_id": "R004", "location": "North Branch", "rating": 1, "review": "This feels like a scam and the billing issue is unacceptable."},
    {"review_id": "R005", "location": "South Branch", "rating": 4, "review": "Clean location and helpful staff. The issue was resolved."},
    {"review_id": "R006", "location": "South Branch", "rating": 3, "review": "Average experience, nothing special to add."},
    {"review_id": "R007", "location": "Jaipur Central", "rating": 2, "review": "Staff were rude and my refund has not arrived."},
    {"review_id": "R008", "location": "North Branch", "rating": 5, "review": "Excellent service, smooth process, and professional team."},
]
if uploaded:
    try:
        source_df = pd.read_csv(uploaded)
        if "review" not in source_df.columns:
            st.error("CSV must contain a column named 'review'.")
            st.stop()
        for col, default in [("review_id", ""), ("location", "Unspecified"), ("rating", None)]:
            if col not in source_df.columns:
                source_df[col] = default
        source_df = source_df.fillna("")
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")
        st.stop()
else:
    source_df = pd.DataFrame(default_reviews)

if source_df.empty:
    st.warning("No reviews found.")
    st.stop()

analysis = source_df["review"].apply(analyze_review).apply(pd.Series)
result = pd.concat([source_df.reset_index(drop=True), analysis], axis=1)
result["draft_response"] = result.apply(lambda r: draft_response(r["review"], r["sentiment"], business_name), axis=1)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Reviews analyzed", len(result))
c2.metric("Negative reviews", int((result["sentiment"] == "Negative").sum()))
c3.metric("High priority", int((result["priority"] == "High").sum()))
c4.metric("Urgent flags", int(result["urgent_flag"].sum()))

st.subheader("Review overview")
col1, col2 = st.columns(2)
with col1:
    st.write("Sentiment distribution")
    st.bar_chart(result["sentiment"].value_counts())
with col2:
    st.write("Priority distribution")
    st.bar_chart(result["priority"].value_counts())

st.subheader("Filter and triage")
f1, f2, f3 = st.columns(3)
sentiment_filter = f1.selectbox("Sentiment", ["All", "Positive", "Neutral", "Negative"])
priority_filter = f2.selectbox("Priority", ["All", "High", "Medium", "Low"])
location_values = ["All"] + sorted([str(x) for x in result["location"].unique()])
location_filter = f3.selectbox("Location", location_values)
filtered = result.copy()
if sentiment_filter != "All":
    filtered = filtered[filtered["sentiment"] == sentiment_filter]
if priority_filter != "All":
    filtered = filtered[filtered["priority"] == priority_filter]
if location_filter != "All":
    filtered = filtered[filtered["location"].astype(str) == location_filter]

display_cols = [c for c in ["review_id","location","rating","review","sentiment","priority","urgent_flag","themes"] if c in filtered.columns]
st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

st.subheader("Draft response review")
if len(filtered):
    choices = filtered.index.tolist()
    chosen = st.selectbox("Choose a review", choices, format_func=lambda idx: f"{result.loc[idx, 'review_id']} • {result.loc[idx, 'sentiment']} • {str(result.loc[idx, 'review'])[:65]}")
    row = result.loc[chosen]
    st.write(f"**Detected themes:** {row['themes']}  |  **Priority:** {row['priority']}  |  **Urgent:** {row['urgent_flag']}")
    edited = st.text_area("Editable reply (human approval required)", row["draft_response"], height=130)
    st.download_button("Download selected reply", data=edited, file_name=f"reply_{row['review_id'] or chosen}.txt", mime="text/plain")
else:
    st.write("No reviews match these filters.")

csv_data = result.to_csv(index=False).encode("utf-8")
st.download_button("Download full analysis CSV", data=csv_data, file_name="review_analysis.csv", mime="text/csv")

with st.expander("Model limitations and production considerations"):
    st.markdown("""
    - This baseline uses keyword counts, not a trained sentiment model; sarcasm, negation, multilingual text, and domain-specific language can cause errors.
    - Urgency flags are rules-based and should be reviewed by a human.
    - Do not upload personal, confidential, or customer-identifying information to this demo.
    - Production version: evaluate a pretrained sentiment classifier, add human feedback, monitor drift, secure access, and integrate platform APIs only with authorization.
    """)
