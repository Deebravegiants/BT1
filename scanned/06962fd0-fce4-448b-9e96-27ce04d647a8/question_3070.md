# Q3070: Header/body injection through read_orb_name (identification.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `read_orb_name` in [src/identification.rs](src/identification.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `read_orb_name` (function)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `read_orb_name` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `read_orb_name` with CR/LF payloads asserting rejection.
