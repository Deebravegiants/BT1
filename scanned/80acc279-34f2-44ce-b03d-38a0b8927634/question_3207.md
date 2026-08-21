# Q3207: Header/body injection through validate (config.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `validate` in [src/config.rs](src/config.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/config.rs](src/config.rs) -> `validate` (function)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `validate` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `validate` with CR/LF payloads asserting rejection.
