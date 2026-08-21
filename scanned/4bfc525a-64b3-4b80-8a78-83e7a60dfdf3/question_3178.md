# Q3178: Header/body injection through default (backend/status.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `default` in [src/backend/status.rs](src/backend/status.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/backend/status.rs](src/backend/status.rs) -> `default` (function)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `default` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `default` with CR/LF payloads asserting rejection.
