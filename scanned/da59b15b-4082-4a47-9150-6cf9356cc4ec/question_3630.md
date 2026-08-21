# Q3630: Concurrent/overlapping sessions through proceed_with_biometric_capture (plans/mod.rs)

## Question
Can an unprivileged attacker cause two signup sessions to overlap in `proceed_with_biometric_capture` in [src/plans/mod.rs](src/plans/mod.rs) (rapid restart, re-scan during capture) so their state interleaves and results are attributed to the wrong session?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `proceed_with_biometric_capture` (function)
- Entrypoint: Restarting or re-triggering the flow while a session is still active
- Attacker controls: timing of the restart relative to in-flight capture and upload tasks
- Exploit idea: Check whether `proceed_with_biometric_capture` holds a session token/generation counter that invalidates late results from a superseded session.
- Invariant to test: Results are accepted only if their session generation matches the active session.
- Expected Immunefi impact: Cross-session attribution of captures and uploads
- Fast validation: Concurrency test: start session B while A's tasks are in flight; assert A's late results are dropped.
