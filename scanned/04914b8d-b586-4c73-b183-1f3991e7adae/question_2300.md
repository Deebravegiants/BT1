# Q2300: Resource limits on the child process in Downstream (livestream/downstream.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `Downstream` in [src/agents/livestream/downstream.rs](src/agents/livestream/downstream.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [src/agents/livestream/downstream.rs](src/agents/livestream/downstream.rs) -> `Downstream` (type)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `Downstream` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `Downstream` asserting limits are applied and enforcement is graceful.
