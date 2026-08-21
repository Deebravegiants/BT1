# Q0854: Header/body injection through Response (backend/s3_region.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `Response` in [src/backend/s3_region.rs](src/backend/s3_region.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/backend/s3_region.rs](src/backend/s3_region.rs) -> `Response` (type)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `Response` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `Response` with CR/LF payloads asserting rejection.
