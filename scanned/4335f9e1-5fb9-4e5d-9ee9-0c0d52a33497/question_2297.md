# Q2297: Ordering assumption in EventReader (livestream/upstream.rs)

## Question
Can an unprivileged attacker exploit `EventReader` in [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) assuming message ordering across channels, so a verdict/state message arriving out of order is applied to the wrong frame or session?

## Target
- File/function: [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) -> `EventReader` (type)
- Entrypoint: Varying per-channel latency through scene complexity
- Attacker controls: relative latency of the channels
- Exploit idea: Check `EventReader` for sequence numbers or explicit ordering enforcement.
- Invariant to test: Cross-channel state application is ordered by explicit sequence, not arrival.
- Expected Immunefi impact: Security state applied to the wrong session or frame
- Fast validation: Concurrency test delivering messages out of order asserting sequence enforcement.
