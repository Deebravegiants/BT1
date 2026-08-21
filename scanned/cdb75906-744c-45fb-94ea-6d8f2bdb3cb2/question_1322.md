# Q1322: Concurrent/overlapping sessions through run (health_check/mod.rs)

## Question
Can an unprivileged attacker cause two signup sessions to overlap in `run` in [src/plans/health_check/mod.rs](src/plans/health_check/mod.rs) (rapid restart, re-scan during capture) so their state interleaves and results are attributed to the wrong session?

## Target
- File/function: [src/plans/health_check/mod.rs](src/plans/health_check/mod.rs) -> `run` (function)
- Entrypoint: Restarting or re-triggering the flow while a session is still active
- Attacker controls: timing of the restart relative to in-flight capture and upload tasks
- Exploit idea: Check whether `run` holds a session token/generation counter that invalidates late results from a superseded session.
- Invariant to test: Results are accepted only if their session generation matches the active session.
- Expected Immunefi impact: Cross-session attribution of captures and uploads
- Fast validation: Concurrency test: start session B while A's tasks are in flight; assert A's late results are dropped.
