# Q2400: Oversized QR payload not length-bounded before parse_output (wpa-supplicant-interface/status.rs)

## Question
Can an unprivileged attacker present a multi-megabyte QR/barcode payload that reaches `parse_output` in [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) unbounded, so the decoded string is copied and retained per frame and drives the Orb into unrecoverable memory pressure that corrupts the in-progress signup state?

## Target
- File/function: [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) -> `parse_output` (function)
- Entrypoint: QR code held in front of the Orb camera during the scan phase
- Attacker controls: full byte content and length of the encoded payload
- Exploit idea: Encode a payload near the QR spec maximum (or a chain of them at frame rate) and check whether `parse_output` bounds length before allocation/parse and whether each rejected payload is dropped promptly.
- Invariant to test: Untrusted decoded QR bytes are length-checked and bounded before any allocation or retention.
- Expected Immunefi impact: Unrecoverable corruption / permanent freeze of the Orb signup state machine
- Fast validation: Fuzz `parse_output` with payload sizes 1B..4MB and assert bounded allocation and constant-time rejection.
