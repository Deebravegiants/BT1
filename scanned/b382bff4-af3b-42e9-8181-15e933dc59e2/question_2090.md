# Q2090: Identifier construction in face_identifier_results allows collision (debug_report.rs)

## Question
Can an unprivileged attacker construct inputs that make `face_identifier_results` in [src/debug_report.rs](src/debug_report.rs) produce an identifier/path colliding with another user's (truncation, delimiter injection, case folding, unicode normalization), so records overwrite or alias each other?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `face_identifier_results` (function)
- Entrypoint: Attacker-controlled identity/session components of the identifier
- Attacker controls: the attacker-supplied substrings composing the identifier
- Exploit idea: Check `face_identifier_results` for length-prefixing/escaping of the components it concatenates.
- Invariant to test: Identifier construction is injective over its component values.
- Expected Immunefi impact: Overwrite or cross-read of another user's biometric records
- Fast validation: Property-test `face_identifier_results` asserting injectivity across component tuples.
