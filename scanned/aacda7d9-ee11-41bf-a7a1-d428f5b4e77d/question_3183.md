# Q3183: Header/body injection through WifiQuality (backend/status.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `WifiQuality` in [src/backend/status.rs](src/backend/status.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/backend/status.rs](src/backend/status.rs) -> `WifiQuality` (type)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `WifiQuality` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `WifiQuality` with CR/LF payloads asserting rejection.
