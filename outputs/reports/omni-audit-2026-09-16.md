# /omni-audit — RCM Denial Analyzer (Scoping Report)

**Date:** 2026-09-16 · **Skill:** `~/.claude/skills/omni-audit/SKILL.md` (alias of `/audit`)

## Applicability Matrix

| Layer | Applies? | Verdict | Coverage |
|---|---|---|---|
| CMS (WordPress etc) | N/A | — | Streamlit standalone |
| Server (LiteSpeed) | N/A | — | Streamlit uvicorn/tornado |
| Hosting (Hostinger) | N/A | — | Deploy target TBD |
| PHP/MySQL | N/A | — | Python/pandas |
| CDN (Cloudflare/S3) | N/A | — | No public assets |
| GA4/GTM | N/A | — | Internal PHI tool, tracking correctly absent |
| Google/Meta Ads | N/A | — | Not customer-facing |
| SEO/AEO/GEO | N/A | — | Not indexed |
| Yoast | N/A | — | No CMS |
| Motion/Animation | **YES** | PASS | /motion-ui pass complete |
| Security/HIPAA | **YES** | PASS | /software-audit iter2 |
| Performance | PARTIAL | — | Streamlit render OK; no CWV path |
| CVE/Deps | **YES** | PASS | pip-audit clean |
| Font Awesome/jQuery/etc | N/A | — | Streamlit native components only |

## Verdict
28/30 layers **N/A** (app is not a marketing website). 2/30 applicable layers **PASS**. `/omni-audit` substance fully covered by prior `/software-audit` + `/audit` + `/motion-ui` passes.

## Additional Findings
None. No new work required.

## Recommendation
For a marketing-site audit, run `/omni-audit` against `theremotereps.com` or similar WordPress stack — that's the intended target profile.
