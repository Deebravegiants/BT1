# Q1139: Ordering assumption in unpack_any (orb-relay-client/lib.rs)

## Question
Can an unprivileged attacker exploit `unpack_any` in [orb-relay-client/src/lib.rs](orb-relay-client/src/lib.rs) assuming message ordering across channels, so a verdict/state message arriving out of order is applied to the wrong frame or session?

## Target
- File/function: [orb-relay-client/src/lib.rs](orb-relay-client/src/lib.rs) -> `unpack_any` (function)
- Entrypoint: Varying per-channel latency through scene complexity
- Attacker controls: relative latency of the channels
- Exploit idea: Check `unpack_any` for sequence numbers or explicit ordering enforcement.
- Invariant to test: Cross-channel state application is ordered by explicit sequence, not arrival.
- Expected Immunefi impact: Security state applied to the wrong session or frame
- Fast validation: Concurrency test delivering messages out of order asserting sequence enforcement.
