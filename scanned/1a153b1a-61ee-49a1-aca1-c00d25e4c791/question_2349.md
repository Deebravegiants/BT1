# Q2349: Oversized QR payload not length-bounded before new (qr_scan/mod.rs)

## Question
Can an unprivileged attacker present a multi-megabyte QR/barcode payload that reaches `new` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) unbounded, so the decoded string is copied and retained per frame and drives the Orb into unrecoverable memory pressure that corrupts the in-progress signup state?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `new` (function)
- Entrypoint: QR code held in front of the Orb camera during the scan phase
- Attacker controls: full byte content and length of the encoded payload
- Exploit idea: Encode a payload near the QR spec maximum (or a chain of them at frame rate) and check whether `new` bounds length before allocation/parse and whether each rejected payload is dropped promptly.
- Invariant to test: Untrusted decoded QR bytes are length-checked and bounded before any allocation or retention.
- Expected Immunefi impact: Unrecoverable corruption / permanent freeze of the Orb signup state machine
- Fast validation: Fuzz `new` with payload sizes 1B..4MB and assert bounded allocation and constant-time rejection.
