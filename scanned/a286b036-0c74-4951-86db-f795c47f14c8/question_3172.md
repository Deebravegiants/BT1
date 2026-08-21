# Q3172: Header/body injection through LocationData (backend/operator_status.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `LocationData` in [src/backend/operator_status.rs](src/backend/operator_status.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/backend/operator_status.rs](src/backend/operator_status.rs) -> `LocationData` (type)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `LocationData` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `LocationData` with CR/LF payloads asserting rejection.
