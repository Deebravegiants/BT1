# Q1228: Non-canonical encoding accepted by parse_output (wpa-supplicant-interface/status.rs)

## Question
Can an unprivileged attacker present a QR whose payload is non-canonically encoded (embedded NUL, mixed-case hex, unicode homoglyph, RTL override, trailing whitespace/newline) so `parse_output` in [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) accepts it and yields an identity/credential value different from what a human or the backend reads?

## Target
- File/function: [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) -> `parse_output` (function)
- Entrypoint: Scanned QR payload during the scan phase
- Attacker controls: exact byte encoding of every field in the QR payload
- Exploit idea: Craft payloads that normalize differently in `parse_output` than in the backend's parser, producing a user/session identity mismatch that survives into the signup.
- Invariant to test: Parsing is canonical and total: exactly one byte string maps to one accepted identity value, with no normalization gap versus the backend.
- Expected Immunefi impact: Signup bound to an identity other than the scanned person's
- Fast validation: Differential test: feed canonical vs. mutated encodings to `parse_output` and assert identical accept/reject and identical extracted fields.
