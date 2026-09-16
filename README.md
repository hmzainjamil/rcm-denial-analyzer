# RCM Denial Analyzer Pro

AI-powered medical claim denial pattern analysis. Streamlit + Claude.

## Live Demo
Deployed on Streamlit Community Cloud.

## Features
- Upload EOB CSV/Excel → AI denial pattern analysis
- Auto-drafts appeal emails (template + AI modes)
- Branded PDF report (reportlab)
- HIPAA/BAA notice + consent gate

## Local Run
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
streamlit run app.py
```

## Required CSV columns
`claim_id, patient_id, payer, denial_code, denial_reason, amount, date, procedure_code`

## Audits
See `outputs/reports/` — software-audit, 15-phase, motion-ui, omni-audit all PASS.

## Security
- API key per-session (never `os.environ`)
- PHI sanitization + prompt-injection guard
- Upload cap 10 MB, column validation, JSON retry
- BAA consent required before AI calls

⚠️ **HIPAA:** Sign BAA with Anthropic before uploading real PHI.
