# Q2247: Resource limits on the child process in sem_getvalue (agentwire/port.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `sem_getvalue` in [agentwire/src/port.rs](agentwire/src/port.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `sem_getvalue` (function)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `sem_getvalue` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `sem_getvalue` asserting limits are applied and enforcement is graceful.
