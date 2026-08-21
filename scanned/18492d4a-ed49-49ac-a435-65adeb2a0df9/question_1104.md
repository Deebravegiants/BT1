# Q1104: Concurrent/overlapping sessions through ExitStrategy (agent/process.rs)

## Question
Can an unprivileged attacker cause two signup sessions to overlap in `ExitStrategy` in [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) (rapid restart, re-scan during capture) so their state interleaves and results are attributed to the wrong session?

## Target
- File/function: [agentwire/src/agent/process.rs](agentwire/src/agent/process.rs) -> `ExitStrategy` (type)
- Entrypoint: Restarting or re-triggering the flow while a session is still active
- Attacker controls: timing of the restart relative to in-flight capture and upload tasks
- Exploit idea: Check whether `ExitStrategy` holds a session token/generation counter that invalidates late results from a superseded session.
- Invariant to test: Results are accepted only if their session generation matches the active session.
- Expected Immunefi impact: Cross-session attribution of captures and uploads
- Fast validation: Concurrency test: start session B while A's tasks are in flight; assert A's late results are dropped.
