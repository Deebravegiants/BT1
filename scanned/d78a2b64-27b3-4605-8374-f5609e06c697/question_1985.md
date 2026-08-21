# Q1985: Header/body injection through SoftwareVersionStatus (backend/signup_post.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `SoftwareVersionStatus` in [src/backend/signup_post.rs](src/backend/signup_post.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/backend/signup_post.rs](src/backend/signup_post.rs) -> `SoftwareVersionStatus` (type)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `SoftwareVersionStatus` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `SoftwareVersionStatus` with CR/LF payloads asserting rejection.
