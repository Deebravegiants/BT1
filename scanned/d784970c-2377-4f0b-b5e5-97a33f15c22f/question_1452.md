# Q1452: Ordering assumption in handle_net_monitor (brokers/observer.rs)

## Question
Can an unprivileged attacker exploit `handle_net_monitor` in [src/brokers/observer.rs](src/brokers/observer.rs) assuming message ordering across channels, so a verdict/state message arriving out of order is applied to the wrong frame or session?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `handle_net_monitor` (function)
- Entrypoint: Varying per-channel latency through scene complexity
- Attacker controls: relative latency of the channels
- Exploit idea: Check `handle_net_monitor` for sequence numbers or explicit ordering enforcement.
- Invariant to test: Cross-channel state application is ordered by explicit sequence, not arrival.
- Expected Immunefi impact: Security state applied to the wrong session or frame
- Fast validation: Concurrency test delivering messages out of order asserting sequence enforcement.
