# Q2421: Long-lived component state in idle_wait_for_button_press not session-scoped (plans/mod.rs)

## Question
Can an unprivileged attacker exploit `idle_wait_for_button_press` in [src/plans/mod.rs](src/plans/mod.rs) holding state across sessions (caches, accumulators, last-value fields) that is read at the start of the next session and treated as belonging to it?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `idle_wait_for_button_press` (function)
- Entrypoint: A session immediately following another user's
- Attacker controls: their session's position in the sequence
- Exploit idea: Enumerate the fields held by `idle_wait_for_button_press` and check which survive session boundaries.
- Invariant to test: No component holds security-relevant state across a session boundary.
- Expected Immunefi impact: Previous user's biometric or verdict state used in the next signup
- Fast validation: Integration test asserting all component state equals its initial value at session start.
