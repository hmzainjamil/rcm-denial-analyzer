# RCM Denial Analyzer

A Streamlit prototype for summarizing medical-claim denial patterns, drafting appeal text, and generating PDF reports from CSV or Excel claim data.

> **Status:** Source inspected; deployment, provider agreements, security controls, and runtime behavior were not verified in this update. Do not use with real patient data or for clinical, billing, or legal decisions without an approved privacy/security review and a validated operating process.

## What the source contains

| Capability | Evidence in repository | Boundary |
|---|---|---|
| CSV/XLSX claim upload with required-column checks and a 10 MB limit | app.py | Source visible; not security-tested |
| Denial-pattern analysis | analyzer.py | Uses an OpenAI-compatible client configured for OpenRouter |
| Template and AI-assisted appeal drafts | email_drafter.py | Drafts require human review; not submission or coverage advice |
| PDF report generation | report_generator.py | Output behavior depends on the running app |
| Streamlit interface | app.py and streamlit_app.py | No live deployment verified |

The AI path may send claim-related fields and free text to OpenRouter. Claim IDs, denial reasons, procedure codes, dates, and amounts can identify people or reveal sensitive information. A consent checkbox does not establish de-identification, a lawful basis, a BAA, or HIPAA compliance.

## Local development

Requires Python and pip.

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    # Set OPENROUTER_API_KEY in .env if using AI features
    streamlit run app.py

These commands follow the repository files; they were not executed in this update. Keep .env out of version control. Use only synthetic or properly de-identified data until deployment, storage, logging, access controls, and provider terms have been reviewed.

## Data and safety

- The app keeps uploaded tables and entered API keys in Streamlit session state during use.
- Source code logs upload row count and filename; filenames may themselves contain sensitive details.
- AI analysis and appeal drafting use OpenRouter configuration, not an Anthropic SDK integration.
- No OpenRouter or Streamlit BAA, retention commitment, deployment control, or HIPAA assessment is established by this repository.
- Appeal drafts can contain unsupported or inaccurate statements. A qualified billing professional must verify every fact and supporting document before use.
- Do not upload PHI, credentials, or identifiable claims to a public demo or unapproved service.

See [SECURITY.md](SECURITY.md) and [data handling notes](docs/DATA_HANDLING.md).

## Validation

The repository contains dated audit reports and a sample dataset, but their presence does not establish current passing tests or independent approval. No tests, deployment, endpoint, or provider review was run for this README update.

## License and support

No license file or documented security contact was present in the inspected repository tree. Reuse terms and a private vulnerability-reporting path are not established.