# Q1108: Ordering assumption in run (agent/thread.rs)

## Question
Can an unprivileged attacker exploit `run` in [agentwire/src/agent/thread.rs](agentwire/src/agent/thread.rs) assuming message ordering across channels, so a verdict/state message arriving out of order is applied to the wrong frame or session?

## Target
- File/function: [agentwire/src/agent/thread.rs](agentwire/src/agent/thread.rs) -> `run` (function)
- Entrypoint: Varying per-channel latency through scene complexity
- Attacker controls: relative latency of the channels
- Exploit idea: Check `run` for sequence numbers or explicit ordering enforcement.
- Invariant to test: Cross-channel state application is ordered by explicit sequence, not arrival.
- Expected Immunefi impact: Security state applied to the wrong session or frame
- Fast validation: Concurrency test delivering messages out of order asserting sequence enforcement.
