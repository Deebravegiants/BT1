# Q3483: Long-lived component state in unpack_any not session-scoped (orb-relay-client/lib.rs)

## Question
Can an unprivileged attacker exploit `unpack_any` in [orb-relay-client/src/lib.rs](orb-relay-client/src/lib.rs) holding state across sessions (caches, accumulators, last-value fields) that is read at the start of the next session and treated as belonging to it?

## Target
- File/function: [orb-relay-client/src/lib.rs](orb-relay-client/src/lib.rs) -> `unpack_any` (function)
- Entrypoint: A session immediately following another user's
- Attacker controls: their session's position in the sequence
- Exploit idea: Enumerate the fields held by `unpack_any` and check which survive session boundaries.
- Invariant to test: No component holds security-relevant state across a session boundary.
- Expected Immunefi impact: Previous user's biometric or verdict state used in the next signup
- Fast validation: Integration test asserting all component state equals its initial value at session start.
