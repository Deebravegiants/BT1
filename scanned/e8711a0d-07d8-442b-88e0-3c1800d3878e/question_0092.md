# Q0092: Resource handle reuse across sessions in detect_face (plans/mod.rs)

## Question
Can an unprivileged attacker exploit `detect_face` in [src/plans/mod.rs](src/plans/mod.rs) reusing a long-lived handle (agent, buffer, file, connection) so residual data belonging to a previous user is present at the start of their session and captured into their record?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `detect_face` (function)
- Entrypoint: Timing a session immediately after another user's
- Attacker controls: ordering of their session relative to the victim's
- Exploit idea: Check `detect_face` for reset/zeroization of reused buffers and handles at session start.
- Invariant to test: Reused resources are zeroized or re-initialized before a new session may read them.
- Expected Immunefi impact: Another user's biometric frames present in the attacker's signup artifacts
- Fast validation: Integration test: fill buffers in session A, assert zeroed at start of session B.
