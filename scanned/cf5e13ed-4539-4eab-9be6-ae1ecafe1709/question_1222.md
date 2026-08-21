# Q1222: Oversized QR payload not length-bounded before Opt (wpa-supplicant-interface/main.rs)

## Question
Can an unprivileged attacker present a multi-megabyte QR/barcode payload that reaches `Opt` in [wpa-supplicant-interface/src/main.rs](wpa-supplicant-interface/src/main.rs) unbounded, so the decoded string is copied and retained per frame and drives the Orb into unrecoverable memory pressure that corrupts the in-progress signup state?

## Target
- File/function: [wpa-supplicant-interface/src/main.rs](wpa-supplicant-interface/src/main.rs) -> `Opt` (type)
- Entrypoint: QR code held in front of the Orb camera during the scan phase
- Attacker controls: full byte content and length of the encoded payload
- Exploit idea: Encode a payload near the QR spec maximum (or a chain of them at frame rate) and check whether `Opt` bounds length before allocation/parse and whether each rejected payload is dropped promptly.
- Invariant to test: Untrusted decoded QR bytes are length-checked and bounded before any allocation or retention.
- Expected Immunefi impact: Unrecoverable corruption / permanent freeze of the Orb signup state machine
- Fast validation: Fuzz `Opt` with payload sizes 1B..4MB and assert bounded allocation and constant-time rejection.
