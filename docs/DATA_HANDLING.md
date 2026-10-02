# Data handling notes

These notes describe source-visible behavior, not a compliance determination or a deployment retention guarantee.

## Input and session state

- The Streamlit app accepts CSV and Excel claim files and stores the parsed table in session state.
- The UI checks for required columns and limits uploads to 10 MB.
- The app also stores the user-entered API key and analysis results in session state.
- Upload logging includes row count and the uploaded filename. Avoid filenames that contain patient or account information.

## External model requests

AI analysis is configured through an OpenAI-compatible client with an OpenRouter base URL. The analysis path sends aggregated denial information, including denial reasons and payer labels. The AI appeal path sends claim-specific fields such as claim ID, payer, denial code/reason, amount, procedure code, and date. Even without a patient_id field, these values and free text may identify a person.

The repository does not establish provider-side retention, a BAA, approved PHI processing, or that the hosted Streamlit environment has appropriate safeguards. Do not send PHI or identifiable claim data to an unapproved provider.

## User acknowledgement and human review

The acknowledgement checkbox is only an interface gate before selected AI actions. It does not establish lawful consent, authorization, de-identification, HIPAA compliance, or contractual coverage.

AI-generated analysis and appeal text can be incomplete or wrong. A qualified human must verify all claim facts, policy references, and supporting evidence. The tool does not submit appeals or determine coverage.

## Retention and deletion

The source stores data in Streamlit session state during the session and logs upload metadata. This repository does not define a complete retention, deletion, backup, incident response, or hosted-platform data lifecycle. Operators must verify those behaviors for each deployment before use.