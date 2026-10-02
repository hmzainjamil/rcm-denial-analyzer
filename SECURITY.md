# Security and data handling

## Scope

This application processes medical claim and payment-related data. Uploaded rows include patient IDs and claim details. The UI sends claim information to OpenRouter for AI analysis and appeal drafting. Do not use identifiable or regulated data unless the deployment owner has separately verified the provider, hosting, privacy, retention, access, and contractual controls for the exact deployment.

## Source-observed boundaries

- The AI analysis request includes total denied amount, denial reasons, and payer values (`analyzer.py`).
- The AI appeal request includes claim ID, payer, denial code/reason, amount, procedure code, and date (`email_drafter.py`).
- The UI says patient IDs are excluded, but this is not true for appeal generation because claim ID is included. Treat this as an unresolved privacy issue.
- The input acknowledgment checkbox is not proof of consent validity, a BAA, or legal compliance.
- The `_sanitize` helper removes a few instruction markers only. It is neither PHI de-identification nor a complete prompt-injection defense.
- Upload size and column checks exist, but comprehensive file safety, deployment retention, access controls, and provider contractual status were not verified.
- Log statements include uploaded filename and row count; exception logging behavior should be reviewed before processing sensitive data.

## Reporting

Contact the repository owner privately with a concise description and redacted reproduction details. Do not publish secrets, patient data, claim identifiers, or sensitive deployment information in a public issue.