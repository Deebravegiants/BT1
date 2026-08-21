# Q0804: Header/body injection through RELAY_BACKEND_URL (backend/endpoints.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `RELAY_BACKEND_URL` in [src/backend/endpoints.rs](src/backend/endpoints.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/backend/endpoints.rs](src/backend/endpoints.rs) -> `RELAY_BACKEND_URL` (item)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `RELAY_BACKEND_URL` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `RELAY_BACKEND_URL` with CR/LF payloads asserting rejection.
