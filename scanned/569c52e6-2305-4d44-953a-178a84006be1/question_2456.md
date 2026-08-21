# Q2456: Late task result accepted after session end in first_file_in_dir (plans/mod.rs)

## Question
Can an unprivileged attacker make a slow task (upload, inference, signing) complete after `first_file_in_dir` in [src/plans/mod.rs](src/plans/mod.rs) has ended the session, so its result is applied to the next user's session?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `first_file_in_dir` (function)
- Entrypoint: Inducing latency in a stage, then ending the session
- Attacker controls: conditions that make the stage slow (scene complexity, payload size)
- Exploit idea: Check for cancellation and generation-checking on all spawned work in `first_file_in_dir`.
- Invariant to test: Session teardown cancels or fences every in-flight task; late results are discarded.
- Expected Immunefi impact: One user's data applied to another user's signup record
- Fast validation: Integration test with an artificially delayed task asserting its result is discarded after teardown.
