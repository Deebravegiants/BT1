# Q3474: Resource limits on the child process in from (livestream-event/lib.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `from` in [livestream-event/src/lib.rs](livestream-event/src/lib.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [livestream-event/src/lib.rs](livestream-event/src/lib.rs) -> `from` (function)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `from` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `from` asserting limits are applied and enforcement is graceful.
