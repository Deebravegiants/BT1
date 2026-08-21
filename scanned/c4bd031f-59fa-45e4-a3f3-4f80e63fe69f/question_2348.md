# Q2348: Non-canonical encoding accepted by poll_extra (qr_scan/mod.rs)

## Question
Can an unprivileged attacker present a QR whose payload is non-canonically encoded (embedded NUL, mixed-case hex, unicode homoglyph, RTL override, trailing whitespace/newline) so `poll_extra` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) accepts it and yields an identity/credential value different from what a human or the backend reads?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `poll_extra` (function)
- Entrypoint: Scanned QR payload during the scan phase
- Attacker controls: exact byte encoding of every field in the QR payload
- Exploit idea: Craft payloads that normalize differently in `poll_extra` than in the backend's parser, producing a user/session identity mismatch that survives into the signup.
- Invariant to test: Parsing is canonical and total: exactly one byte string maps to one accepted identity value, with no normalization gap versus the backend.
- Expected Immunefi impact: Signup bound to an identity other than the scanned person's
- Fast validation: Differential test: feed canonical vs. mutated encodings to `poll_extra` and assert identical accept/reject and identical extracted fields.
