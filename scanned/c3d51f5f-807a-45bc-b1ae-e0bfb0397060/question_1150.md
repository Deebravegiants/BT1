# Q1150: Long-lived component state in wait_for_msg not session-scoped (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker exploit `wait_for_msg` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) holding state across sessions (caches, accumulators, last-value fields) that is read at the start of the next session and treated as belonging to it?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `wait_for_msg` (function)
- Entrypoint: A session immediately following another user's
- Attacker controls: their session's position in the sequence
- Exploit idea: Enumerate the fields held by `wait_for_msg` and check which survive session boundaries.
- Invariant to test: No component holds security-relevant state across a session boundary.
- Expected Immunefi impact: Previous user's biometric or verdict state used in the next signup
- Fast validation: Integration test asserting all component state equals its initial value at session start.
