# Q2299: Resource limits on the child process in push (livestream/downstream.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `push` in [src/agents/livestream/downstream.rs](src/agents/livestream/downstream.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [src/agents/livestream/downstream.rs](src/agents/livestream/downstream.rs) -> `push` (function)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `push` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `push` asserting limits are applied and enforcement is graceful.
