# Q1101: Long-lived component state in spawn_process_impl not session-scoped (agent/process.rs)

## Question
Can an unprivileged attacker exploit `spawn_process_impl` in [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) holding state across sessions (caches, accumulators, last-value fields) that is read at the start of the next session and treated as belonging to it?

## Target
- File/function: [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) -> `spawn_process_impl` (function)
- Entrypoint: A session immediately following another user's
- Attacker controls: their session's position in the sequence
- Exploit idea: Enumerate the fields held by `spawn_process_impl` and check which survive session boundaries.
- Invariant to test: No component holds security-relevant state across a session boundary.
- Expected Immunefi impact: Previous user's biometric or verdict state used in the next signup
- Fast validation: Integration test asserting all component state equals its initial value at session start.
