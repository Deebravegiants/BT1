# Q3465: Long-lived component state in poll_next not session-scoped (livestream/upstream.rs)

## Question
Can an unprivileged attacker exploit `poll_next` in [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) holding state across sessions (caches, accumulators, last-value fields) that is read at the start of the next session and treated as belonging to it?

## Target
- File/function: [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) -> `poll_next` (function)
- Entrypoint: A session immediately following another user's
- Attacker controls: their session's position in the sequence
- Exploit idea: Enumerate the fields held by `poll_next` and check which survive session boundaries.
- Invariant to test: No component holds security-relevant state across a session boundary.
- Expected Immunefi impact: Previous user's biometric or verdict state used in the next signup
- Fast validation: Integration test asserting all component state equals its initial value at session start.
