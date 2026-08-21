# Q1111: Long-lived component state in default not session-scoped (agents/mod.rs)

## Question
Can an unprivileged attacker exploit `default` in [src/agents/mod.rs](src/agents/mod.rs) holding state across sessions (caches, accumulators, last-value fields) that is read at the start of the next session and treated as belonging to it?

## Target
- File/function: [src/agents/mod.rs](src/agents/mod.rs) -> `default` (function)
- Entrypoint: A session immediately following another user's
- Attacker controls: their session's position in the sequence
- Exploit idea: Enumerate the fields held by `default` and check which survive session boundaries.
- Invariant to test: No component holds security-relevant state across a session boundary.
- Expected Immunefi impact: Previous user's biometric or verdict state used in the next signup
- Fast validation: Integration test asserting all component state equals its initial value at session start.
