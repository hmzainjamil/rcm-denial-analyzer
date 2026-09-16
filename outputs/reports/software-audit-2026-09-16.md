# /software-audit — RCM Denial Analyzer (Critical Level)

**Date:** 2026-09-16
**Target:** ~/Downloads/digiminds/rcm-denial-analyzer
**Files:** app.py, analyzer.py, email_drafter.py, report_generator.py
**Scope:** Phase 2/4/5/6 + Security + AI (physical/safety N/A)
**Gates:** SECURITY, INTEGRITY, PRODUCTION (non-compensable) · SAFETY (N/A)

## Pre-check
- Claim: report_generator.py:160-183 duplicate pat_tbl → **FALSE**. Lines are legitimate patterns table + fix-actions loop. Skipped.

## Gate Scores (Iteration 1 — before fixes)

| Gate | Status | Findings |
|---|---|---|
| SECURITY | **FAIL** | PHI→Anthropic w/o BAA disclosure; env-var key leak across users; unsafe_allow_html; no upload size cap |
| INTEGRITY | **FAIL** | No CSV column validation; malformed-JSON retry absent; unbounded API loop cost |
| PRODUCTION | **FAIL** | Hallucinated model ID `claude-sonnet-4-6`; no logging; no rate limit; blocking UI on N-row API calls |
| SAFETY | N/A | Web app, no physical path |

## Critical Findings

### F1 SECURITY-CRIT: PHI transmitted to LLM w/o BAA notice
- **Where:** analyzer.py:11-89, email_drafter.py:153-170, app.py:194
- **Risk:** HIPAA violation. patient_id + claim details sent to `api.anthropic.com` without displayed Business Associate Agreement warning
- **Fix:** Add prominent BAA disclosure + user consent checkbox before AI calls; strip patient_id from prompts by default

### F2 SECURITY-CRIT: API key process-wide contamination
- **Where:** app.py:31 `os.environ["ANTHROPIC_API_KEY"] = api_key`
- **Risk:** Streamlit multi-user shared instance: User A's key leaks to User B
- **Fix:** Store in `st.session_state["api_key"]`, pass explicitly to funcs

### F3 PRODUCTION-CRIT: Invalid model ID
- **Where:** analyzer.py:79, email_drafter.py:166 `model="claude-sonnet-4-6"`
- **Risk:** Runtime `NotFoundError` — model does not exist. App broken end-to-end
- **Fix:** Use `claude-sonnet-4-5` (or current valid ID)

### F4 SECURITY-HIGH: No upload size/type validation
- **Where:** app.py:80-85
- **Risk:** DoS via 10GB CSV; malicious xlsx macros; path traversal
- **Fix:** `if uploaded.size > 10_000_000: reject`; validate MIME

### F5 INTEGRITY-HIGH: Missing column validation
- **Where:** app.py:88 `df["amount"]`
- **Risk:** `KeyError` crash on malformed CSV (required cols absent)
- **Fix:** Validate required cols present before use, friendly error

### F6 INTEGRITY-HIGH: LLM JSON parse fragile
- **Where:** analyzer.py:84-89
- **Risk:** `json.JSONDecodeError` uncaught; no retry; user sees stacktrace
- **Fix:** try/except JSONDecodeError, one retry, fallback to empty structure

### F7 PRODUCTION-HIGH: Unbounded per-row API loop
- **Where:** app.py:192-207 loops `df.iterrows()` calling `generate_ai_appeal` per claim
- **Risk:** 1000-row CSV = 1000 API calls = $$$ + 10+ min block
- **Fix:** Cap N ≤ 25 with warning; batch or progress bar

### F8 AI-HIGH: Prompt injection via denial_reason
- **Where:** analyzer.py:35 `json.dumps(denial_summary)` embeds user-controlled text
- **Risk:** Attacker crafts denial_reason to override instructions
- **Fix:** Sanitize or wrap user data in explicit delimiters + instruction override guard

### F9 SECURITY-MED: unsafe_allow_html
- **Where:** app.py:21, 281
- **Risk:** static HTML currently — but pattern encourages XSS if company_name ever reflected
- **Fix:** Escape company_name if ever embedded in unsafe_allow_html blocks

### F10 PRODUCTION-MED: No logging/telemetry
- **Fix:** Add `logging` module, log API errors + upload events (no PHI)

## Non-compensable Gate Verdict (Iteration 1)
- **SECURITY: FAIL** (F1, F2, F4)
- **INTEGRITY: FAIL** (F5, F6)
- **PRODUCTION: FAIL** (F3, F7)
- **Overall: FAIL — MUST FIX**

## Iteration 2 (after fixes applied — see commits)
See `software-audit-2026-09-16-iter2.md` after fix pass.
