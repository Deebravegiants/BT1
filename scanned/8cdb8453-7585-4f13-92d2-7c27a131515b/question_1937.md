# Q1937: Header/body injection through decrypt_and_unseal (agents/image_notary.rs)

## Question
Can an unprivileged attacker embed CR/LF or header-delimiter bytes in a field that `decrypt_and_unseal` in [src/agents/image_notary.rs](src/agents/image_notary.rs) places into a request header or multipart body, injecting attacker-chosen headers or parts into the upload request?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `decrypt_and_unseal` (function)
- Entrypoint: Attacker-influenced metadata fields in the upload path
- Attacker controls: raw bytes of the metadata field
- Exploit idea: Check `decrypt_and_unseal` for validation of header/part values built from session data.
- Invariant to test: Header and multipart values are validated to exclude structural delimiters.
- Expected Immunefi impact: Attacker-controlled request structure for biometric uploads
- Fast validation: Unit-test `decrypt_and_unseal` with CR/LF payloads asserting rejection.
