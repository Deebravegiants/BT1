# Q3126: Header/body injection through from_str (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `from_str` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `from_str` (function)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `from_str` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `from_str` with CR/LF payloads asserting rejection.
