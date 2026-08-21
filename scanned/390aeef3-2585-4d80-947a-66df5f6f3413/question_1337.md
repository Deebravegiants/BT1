# Q1337: Ordering assumption in handle_ir_net (brokers/orb.rs)

## Question
Can an unprivileged attacker exploit `handle_ir_net` in [src/brokers/orb.rs](src/brokers/orb.rs) assuming message ordering across channels, so a verdict/state message arriving out of order is applied to the wrong frame or session?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `handle_ir_net` (function)
- Entrypoint: Varying per-channel latency through scene complexity
- Attacker controls: relative latency of the channels
- Exploit idea: Check `handle_ir_net` for sequence numbers or explicit ordering enforcement.
- Invariant to test: Cross-channel state application is ordered by explicit sequence, not arrival.
- Expected Immunefi impact: Security state applied to the wrong session or frame
- Fast validation: Concurrency test delivering messages out of order asserting sequence enforcement.
