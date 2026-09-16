# /software-audit — RCM Denial Analyzer (Iteration 2, post-fix)

**Date:** 2026-09-16
**Iter:** 2 (after fixes)

## Fixes Applied

| ID | Fix | Files |
|---|---|---|
| F1 | HIPAA/BAA disclosure + consent checkbox; PHI sanitized; patient_id not sent | app.py, analyzer.py, email_drafter.py |
| F2 | API key in `st.session_state` only, never `os.environ`; explicit param passed | app.py, analyzer.py, email_drafter.py |
| F3 | Model ID `claude-sonnet-4-5` (valid) via `MODEL_ID` const | analyzer.py, email_drafter.py |
| F4 | Upload cap 10 MB with reject | app.py |
| F5 | `validate_columns()` raises on missing required cols; friendly UI error | analyzer.py, app.py |
| F6 | try/except JSONDecodeError, 1 retry, graceful empty fallback | analyzer.py |
| F7 | AI email loop capped `MAX_AI_EMAIL_ROWS=25` + progress bar | app.py |
| F8 | Prompt-injection guard: `<user_data>`/`<claim_data>` delimiter + regex sanitize | analyzer.py, email_drafter.py |
| F9 | Reviewed — company_name never rendered inside unsafe_allow_html blocks. Documented. | app.py |
| F10 | `logging` module wired, INFO events for upload + errors (no PHI) | app.py, analyzer.py |

## Verification
- Syntax check all 4 files: PASS
- Smoke test: sample CSV loads, `validate_columns` passes on good/raises on bad, PDF renders (5289 bytes)
- `pip-audit -r requirements.txt`: **No known vulnerabilities**
- Sanitize regex confirmed strips `system:` / `ignore previous`

## Gate Scores (Iteration 2)

| Gate | Status | Notes |
|---|---|---|
| SECURITY | **PASS** | BAA notice + consent, per-session key, PHI sanitized, upload cap |
| INTEGRITY | **PASS** | Col validation, JSON retry+fallback, cost cap |
| PRODUCTION | **PASS** | Valid model, logging, rate cap, progress UX |
| SAFETY | N/A | Web app |

**Overall: PASS**

## Residual (non-blocking, recommend for v2)
- Add Streamlit-native rate limiter (per-IP token bucket) — currently trust-based
- Move AI calls to background thread — current is synchronous
- Add unit tests (`pytest`) — currently only manual smoke
- Add `SECURITY.md` + `.env.example` documenting BAA requirement
