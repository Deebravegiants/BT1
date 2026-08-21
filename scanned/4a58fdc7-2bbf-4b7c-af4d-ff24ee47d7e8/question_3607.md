# Q3607: Ordering assumption in handle_user_qr_code (plans/mod.rs)

## Question
Can an unprivileged attacker exploit `handle_user_qr_code` in [src/plans/mod.rs](src/plans/mod.rs) assuming message ordering across channels, so a verdict/state message arriving out of order is applied to the wrong frame or session?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `handle_user_qr_code` (function)
- Entrypoint: Varying per-channel latency through scene complexity
- Attacker controls: relative latency of the channels
- Exploit idea: Check `handle_user_qr_code` for sequence numbers or explicit ordering enforcement.
- Invariant to test: Cross-channel state application is ordered by explicit sequence, not arrival.
- Expected Immunefi impact: Security state applied to the wrong session or frame
- Fast validation: Concurrency test delivering messages out of order asserting sequence enforcement.
