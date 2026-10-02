# Security

## Current status

This repository is a prototype that may process claim data. It has not been certified for HIPAA compliance, production PHI handling, or secure deployment. Do not use real patient data unless the deploying organization has completed its own security, privacy, contractual, and operational approval.

The UI acknowledgement checkbox is not a security control, de-identification method, legal consent, or proof of a Business Associate Agreement.

## Reporting a vulnerability

Do not include PHI, credentials, tokens, or exploit details in a public issue. The repository does not document a dedicated private security contact. If GitHub private vulnerability reporting is enabled for this repository, use that channel; otherwise ask the maintainer to provide a private reporting route before sharing sensitive details.

## Secret handling

- Use a local untracked environment file for OPENROUTER_API_KEY.
- Never paste real credentials into README files, issues, reports, screenshots, or logs.
- Revoke and rotate any credential that is exposed.

## Data handling

See [docs/DATA_HANDLING.md](docs/DATA_HANDLING.md). Before any deployment, review authentication and authorization, session isolation, log destination and retention, upload handling, outbound provider requests, backup, deletion, and access controls.