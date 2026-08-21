# Q1879: Header/body injection through gen_salt (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `gen_salt` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `gen_salt` (function)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `gen_salt` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `gen_salt` with CR/LF payloads asserting rejection.
