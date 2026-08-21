# Q1391: Resource handle reuse across sessions in set_fisheye (brokers/orb.rs)

## Question
Can an unprivileged attacker exploit `set_fisheye` in [src/brokers/orb.rs](src/brokers/orb.rs) reusing a long-lived handle (agent, buffer, file, connection) so residual data belonging to a previous user is present at the start of their session and captured into their record?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `set_fisheye` (function)
- Entrypoint: Timing a session immediately after another user's
- Attacker controls: ordering of their session relative to the victim's
- Exploit idea: Check `set_fisheye` for reset/zeroization of reused buffers and handles at session start.
- Invariant to test: Reused resources are zeroized or re-initialized before a new session may read them.
- Expected Immunefi impact: Another user's biometric frames present in the attacker's signup artifacts
- Fast validation: Integration test: fill buffers in session A, assert zeroed at start of session B.
