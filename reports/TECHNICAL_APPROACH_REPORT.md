# Technical Approach Report: Revio AI Review Intelligence
**Assessment:** Cynbit AI/ML Engineer Intern  
**Status:** Prototype design and implementation  
**Date:** 17 October 2026

## 1. System objective
Build a review-processing assistant that converts review text into useful operational signals: sentiment, broad themes, urgency/priority, and an editable response draft. The prototype is intentionally local and uses synthetic sample data.

## 2. Architecture and data pipeline
```text
CSV upload / sample dataset
        |
        v
Schema validation and basic cleaning
        |
        v
Text normalization and feature extraction
        |
        +--> Keyword sentiment baseline
        +--> Theme rules
        +--> Conservative urgency rules
        |
        v
Priority queue + draft response templates
        |
        v
Human review / edit / CSV export
```

### Data schema
- `review_id`: optional identifier.
- `location`: optional branch or location.
- `rating`: optional numeric rating.
- `review`: required text.
The demo does not require user names, email addresses, phone numbers, or other identifying data.

## 3. Model choices
### Current PoC
A transparent lexicon/keyword baseline is implemented in `app.py`. It counts positive and negative terms, detects a small set of themes, and applies conservative urgency rules. Response drafts use controlled templates.

**Why this choice:** fast to run, no API key, low cost, explainable, and suitable for demonstrating end-to-end workflow under assessment time constraints.

**Limitations:** brittle with negation, sarcasm, mixed sentiment, multilingual text, spelling variations, and context. It must not be represented as a production-ready ML model.

### Production candidate
Benchmark a pretrained sentiment classifier suitable for the review language(s), such as a compact transformer from the Hugging Face ecosystem, against the baseline. Select based on measured macro-F1, per-class recall, inference latency, cost, licensing, and deployment constraints. Add a separate classifier or multilabel model for topics if labeled data supports it.

For response generation, begin with approved templates and structured fields. If an LLM is introduced later, use a controlled prompt, provide only the review and approved business policy, require the model to avoid unsupported promises, and require human approval. Do not fine-tune until the evaluation set and data rights are clear.

## 4. Prompt / response design
The current demo uses templates rather than a generative model, which avoids hidden API dependencies and limits unsupported claims.

Suggested future system instruction:
> You are a customer-support drafting assistant. Write a concise, empathetic response based only on the supplied review and approved response policy. Do not invent facts, claim an issue is resolved, request personal information publicly, or promise compensation. For safety, fraud, privacy, legal, or serious billing concerns, do not draft a substantive public resolution; recommend escalation to a human reviewer. Output a draft only; do not publish it.

Prompt inputs should be structured:
- Review text (redacted where possible)
- Sentiment and model confidence
- Detected themes and urgency flags
- Approved response policy and tone
- Output schema with `draft`, `escalation_required`, and `reason`

Validate the output schema and apply policy checks before presenting the draft. Treat review text as untrusted data, not as instructions to the model.

## 5. Evaluation
1. Build a labeled set using authorized historical or synthetic reviews.
2. Split by time or business/location where feasible to reduce leakage.
3. Compare keyword baseline with pretrained model.
4. Measure sentiment macro-F1 and per-class metrics.
5. Measure urgency recall separately; manually review every false negative in the high-risk category.
6. Conduct blinded human review of response tone, factuality, and usefulness.
7. Track p50/p95 latency, errors, cost, and reviewer edit/acceptance rate.
8. Set launch thresholds with product and operations stakeholders before pilot.

## 6. Security, privacy, and responsible AI
- Use synthetic data for demos; only process customer data with authorization.
- Minimize and redact personal data.
- Store secrets in environment variables or a secrets manager; never commit API keys.
- Use authentication, role-based access, audit trails, retention rules, and encryption for production.
- Require human review for high-risk content and all public responses during the pilot.
- Monitor language-specific errors and model drift.
- Keep an explicit fallback when model/API calls fail.

## 7. Execution plan
| Phase | Work | Exit criterion |
|---|---|---|
| 1. Discovery | Confirm review sources, languages, policy, risk classes, baseline workload | Stakeholder-approved requirements |
| 2. Data | Collect authorized sample, redact PII, label a benchmark | Reviewed dataset and label guide |
| 3. Baseline | Run current keyword prototype and document errors | Reproducible baseline metrics |
| 4. Model benchmark | Compare pretrained sentiment/topic models | Model card with quality/latency/cost |
| 5. Workflow pilot | Add reviewer queue, audit log, feedback capture | Human approval flow works end-to-end |
| 6. Controlled rollout | Integrate authorized platform APIs, monitor and evaluate | Acceptance thresholds met; rollback available |

## 8. Run instructions
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 9. Limitations
This prototype is not connected to Cynbit systems or live review platforms. The sentiment logic is a rule-based baseline rather than a trained classifier. The reports describe a proposed opportunity and implementation plan, not verified internal requirements or realized business outcomes.
