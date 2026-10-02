# RCM Denial Analyzer

> Streamlit application for reviewing denial summaries and drafting appeal text from uploaded EOB or claims data.
>
> **Status:** Source tree present; deployment, external provider terms, and production readiness not verified.

## Purpose and scope

The application accepts CSV or Excel claim rows, computes summaries, can request narrative analysis and appeal drafts through OpenRouter, and can generate a PDF report. It is an aid for review. Generated recovery estimates, analysis, and appeal language need qualified human review against the source claim and payer rules.

This repository handles medical and financial claim fields, including `patient_id`, claim identifiers, payer, denial reasons, amounts, dates, and procedure codes. Do not upload identifiable or regulated data unless the deployment owner has independently verified the complete provider, hosting, privacy, retention, and contractual controls for that exact deployment. This README does not establish HIPAA compliance or a Business Associate Agreement.

## Current implementation

| Capability | Source evidence | Boundary |
|---|---|---|
| CSV/XLSX upload and required-column validation | `app.py`, `analyzer.py` | UI limits uploads to 10 MB; this is not a complete file-safety control. |
| Denial summaries and narrative analysis | `analyzer.py` | Sends aggregate amounts, denial reasons, and payer values to OpenRouter. These fields may remain identifying or sensitive. |
| Appeal text generation | `email_drafter.py`, `app.py` | Sends claim ID, payer, denial details, amount, procedure, and date to OpenRouter for each selected claim. |
| PDF and text downloads | `report_generator.py`, `app.py` | Exports are user-triggered; generated content is not independently validated. |
| Sample input | `sample_data/sample_eob.csv` | Use only after inspecting the sample contents and current code. |

## Setup

Requirements are listed in `requirements.txt`. The current source uses Streamlit and the OpenAI-compatible client pointed at OpenRouter. The repository's older Anthropic command is stale. The application accepts an OpenRouter key through its UI or `OPENROUTER_API_KEY`; do not put a live key in shell history or committed files.

The repository includes `streamlit_app.py` and `app.py`; the canonical entry point and deployment target have not been established here. Confirm the current deployment configuration before following deployment instructions. No installation, build, or runtime check was performed for this documentation update.

## Data and security notes

- The UI displays a notice and acknowledgment checkbox, but the checkbox is not proof of a provider contract or legal compliance.
- Current OpenRouter prompts omit `patient_id`. `analyzer.py` sends aggregate totals, denial codes/reasons, and payer values; `email_drafter.py` sends claim ID, payer, denial code/reason, amount, procedure, and date. Template-based appeal emails are generated locally and can include `patient_id`.
- `_sanitize` removes a small set of instruction-like strings; it is not PHI de-identification or a reliable prompt-injection defense.
- Uploads are parsed in the Streamlit process. The README's in-memory-only claim has not been verified against hosting, logs, crash reporting, or deployment behavior.
- Application logs record upload row counts and filenames; error paths may also record exception details. Do not treat these logs as a validated audit trail.
- No license file was present in the inspected repository tree. Licensing status is unspecified.

Report security or privacy concerns privately to the repository owner. Avoid posting claim examples, keys, patient data, or deployment details in public issues.

## Repository map

- `app.py` — Streamlit interface and workflow
- `analyzer.py` — denial summaries and OpenRouter request
- `email_drafter.py` — template and AI appeal text
- `report_generator.py` — PDF generation
- `sample_data/` — sample EOB input
- `outputs/reports/` — historical audit documents; not current independent certification

## Verification status

The README, application, analyzer, appeal generator, dependency manifest, sample configuration paths, and recursive file tree were inspected on 2026-10-02. Historical audit reports are repository artifacts only; no audit pass or compliance conclusion is asserted here. No tests, provider calls, deployment checks, or PHI-handling assessment were performed.