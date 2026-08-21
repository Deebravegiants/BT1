# Q0849: Header/body injection through TieredPackageRequest (backend/presigned_url.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `TieredPackageRequest` in [src/backend/presigned_url.rs](src/backend/presigned_url.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/backend/presigned_url.rs](src/backend/presigned_url.rs) -> `TieredPackageRequest` (type)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `TieredPackageRequest` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `TieredPackageRequest` with CR/LF payloads asserting rejection.
