# Q3762: Long-lived component state in Builder not session-scoped (brokers/orb.rs)

## Question
Can an unprivileged attacker exploit `Builder` in [src/brokers/orb.rs](src/brokers/orb.rs) holding state across sessions (caches, accumulators, last-value fields) that is read at the start of the next session and treated as belonging to it?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `Builder` (type)
- Entrypoint: A session immediately following another user's
- Attacker controls: their session's position in the sequence
- Exploit idea: Enumerate the fields held by `Builder` and check which survive session boundaries.
- Invariant to test: No component holds security-relevant state across a session boundary.
- Expected Immunefi impact: Previous user's biometric or verdict state used in the next signup
- Fast validation: Integration test asserting all component state equals its initial value at session start.
