# Q3816: Late task result accepted after session end in run (bin/orb-core.rs)

## Question
Can an unprivileged attacker make a slow task (upload, inference, signing) complete after `run` in [src/bin/orb-core.rs](src/bin/orb-core.rs) has ended the session, so its result is applied to the next user's session?

## Target
- File/function: [src/bin/orb-core.rs](src/bin/orb-core.rs) -> `run` (function)
- Entrypoint: Inducing latency in a stage, then ending the session
- Attacker controls: conditions that make the stage slow (scene complexity, payload size)
- Exploit idea: Check for cancellation and generation-checking on all spawned work in `run`.
- Invariant to test: Session teardown cancels or fences every in-flight task; late results are discarded.
- Expected Immunefi impact: One user's data applied to another user's signup record
- Fast validation: Integration test with an artificially delayed task asserting its result is discarded after teardown.
