# Q1476: Concurrent/overlapping sessions through spawn (ui/mod.rs)

## Question
Can an unprivileged attacker cause two signup sessions to overlap in `spawn` in [src/ui/mod.rs](src/ui/mod.rs) (rapid restart, re-scan during capture) so their state interleaves and results are attributed to the wrong session?

## Target
- File/function: [src/ui/mod.rs](src/ui/mod.rs) -> `spawn` (function)
- Entrypoint: Restarting or re-triggering the flow while a session is still active
- Attacker controls: timing of the restart relative to in-flight capture and upload tasks
- Exploit idea: Check whether `spawn` holds a session token/generation counter that invalidates late results from a superseded session.
- Invariant to test: Results are accepted only if their session generation matches the active session.
- Expected Immunefi impact: Cross-session attribution of captures and uploads
- Fast validation: Concurrency test: start session B while A's tasks are in flight; assert A's late results are dropped.
