# Revio AI Review Intelligence — Cynbit Assessment PoC

A small, runnable proof of concept aligned with Cynbit's publicly described Revio review-management product. It triages sample customer reviews using a transparent keyword baseline, flags potentially urgent feedback, detects broad themes, and drafts editable response suggestions.

## Features
- Streamlit web UI
- CSV upload (required column: `review`; optional: `review_id`, `location`, `rating`)
- Sentiment baseline: positive / neutral / negative
- Rules-based priority and urgency flags
- Basic theme detection
- Human-editable reply suggestions
- CSV export

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Input CSV example
```csv
review_id,location,rating,review
A01,Jaipur Central,1,"I was charged twice and support was slow."
A02,North Branch,5,"Excellent service and friendly staff."
```

## Architecture
CSV/sample data → validation → keyword/rule-based feature extraction → sentiment and priority labels → response draft → human review/export.

## Important limitations
This is a baseline prototype, not a production sentiment system and not connected to Cynbit's internal data or live review platforms. Keyword methods can miss negation, sarcasm, context, and non-English text. The generated replies are suggestions only and should not be auto-published. No live customer data or API credentials are included.

## Next steps for production
1. Define labels and evaluation set with domain experts.
2. Benchmark a pretrained sentiment classifier against the keyword baseline.
3. Add multilingual support, confidence thresholds, and human correction capture.
4. Integrate review platforms only with explicit authorization and secure OAuth/API credential management.
5. Track macro-F1, urgent-case recall, response acceptance rate, latency, and cost.
6. Add authentication, role-based access, audit logs, rate limits, privacy controls, and monitoring.

## Assessment context
The opportunity analysis and technical approach are in `reports/`. Synthetic sample reviews are in `data/sample_reviews.csv`.
