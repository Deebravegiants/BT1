# Q1172: Long-lived component state in PollerAgent not session-scoped (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker exploit `PollerAgent` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) holding state across sessions (caches, accumulators, last-value fields) that is read at the start of the next session and treated as belonging to it?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `PollerAgent` (type)
- Entrypoint: A session immediately following another user's
- Attacker controls: their session's position in the sequence
- Exploit idea: Enumerate the fields held by `PollerAgent` and check which survive session boundaries.
- Invariant to test: No component holds security-relevant state across a session boundary.
- Expected Immunefi impact: Previous user's biometric or verdict state used in the next signup
- Fast validation: Integration test asserting all component state equals its initial value at session start.
