# Q2019: Header/body injection through Request (backend/presigned_url.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `Request` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `Request` (type)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `Request` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `Request` with CR/LF payloads asserting rejection.
