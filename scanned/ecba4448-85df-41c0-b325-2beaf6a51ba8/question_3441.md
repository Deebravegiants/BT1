# Q3441: Ordering assumption in exit_strategy (agent/process.rs)

## Question
Can an unprivileged attacker exploit `exit_strategy` in [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) assuming message ordering across channels, so a verdict/state message arriving out of order is applied to the wrong frame or session?

## Target
- File/function: [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) -> `exit_strategy` (function)
- Entrypoint: Varying per-channel latency through scene complexity
- Attacker controls: relative latency of the channels
- Exploit idea: Check `exit_strategy` for sequence numbers or explicit ordering enforcement.
- Invariant to test: Cross-channel state application is ordered by explicit sequence, not arrival.
- Expected Immunefi impact: Security state applied to the wrong session or frame
- Fast validation: Concurrency test delivering messages out of order asserting sequence enforcement.
