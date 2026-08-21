# Q1089: Long-lived component state in is_initialized not session-scoped (agent/mod.rs)

## Question
Can an unprivileged attacker exploit `is_initialized` in [agentwire/src/agent/mod.rs](agentwire/src/agent/mod.rs) holding state across sessions (caches, accumulators, last-value fields) that is read at the start of the next session and treated as belonging to it?

## Target
- File/function: [agentwire/src/agent/mod.rs](agentwire/src/agent/mod.rs) -> `is_initialized` (function)
- Entrypoint: A session immediately following another user's
- Attacker controls: their session's position in the sequence
- Exploit idea: Enumerate the fields held by `is_initialized` and check which survive session boundaries.
- Invariant to test: No component holds security-relevant state across a session boundary.
- Expected Immunefi impact: Previous user's biometric or verdict state used in the next signup
- Fast validation: Integration test asserting all component state equals its initial value at session start.
