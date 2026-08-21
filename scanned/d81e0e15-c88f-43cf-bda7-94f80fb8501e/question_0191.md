# Q0191: Concurrent/overlapping sessions through recalibrate (brokers/orb.rs)

## Question
Can an unprivileged attacker cause two signup sessions to overlap in `recalibrate` in [src/brokers/orb.rs](src/brokers/orb.rs) (rapid restart, re-scan during capture) so their state interleaves and results are attributed to the wrong session?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `recalibrate` (function)
- Entrypoint: Restarting or re-triggering the flow while a session is still active
- Attacker controls: timing of the restart relative to in-flight capture and upload tasks
- Exploit idea: Check whether `recalibrate` holds a session token/generation counter that invalidates late results from a superseded session.
- Invariant to test: Results are accepted only if their session generation matches the active session.
- Expected Immunefi impact: Cross-session attribution of captures and uploads
- Fast validation: Concurrency test: start session B while A's tasks are in flight; assert A's late results are dropped.
