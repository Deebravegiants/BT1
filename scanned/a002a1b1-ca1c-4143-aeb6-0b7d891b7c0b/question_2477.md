# Q2477: Late task result accepted after session end in Plan (plans/idle.rs)

## Question
Can an unprivileged attacker make a slow task (upload, inference, signing) complete after `Plan` in [src/plans/idle.rs](src/plans/idle.rs) has ended the session, so its result is applied to the next user's session?

## Target
- File/function: [src/plans/idle.rs](src/plans/idle.rs) -> `Plan` (type)
- Entrypoint: Inducing latency in a stage, then ending the session
- Attacker controls: conditions that make the stage slow (scene complexity, payload size)
- Exploit idea: Check for cancellation and generation-checking on all spawned work in `Plan`.
- Invariant to test: Session teardown cancels or fences every in-flight task; late results are discarded.
- Expected Immunefi impact: One user's data applied to another user's signup record
- Fast validation: Integration test with an artificially delayed task asserting its result is discarded after teardown.
