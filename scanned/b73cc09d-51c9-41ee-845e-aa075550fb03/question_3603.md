# Q3603: Ordering assumption in scan_remaining_qr_codes (plans/mod.rs)

## Question
Can an unprivileged attacker exploit `scan_remaining_qr_codes` in [src/plans/mod.rs](src/plans/mod.rs) assuming message ordering across channels, so a verdict/state message arriving out of order is applied to the wrong frame or session?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `scan_remaining_qr_codes` (function)
- Entrypoint: Varying per-channel latency through scene complexity
- Attacker controls: relative latency of the channels
- Exploit idea: Check `scan_remaining_qr_codes` for sequence numbers or explicit ordering enforcement.
- Invariant to test: Cross-channel state application is ordered by explicit sequence, not arrival.
- Expected Immunefi impact: Security state applied to the wrong session or frame
- Fast validation: Concurrency test delivering messages out of order asserting sequence enforcement.
