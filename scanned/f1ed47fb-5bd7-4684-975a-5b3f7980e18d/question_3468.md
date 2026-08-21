# Q3468: Resource limits on the child process in Event (livestream/upstream.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `Event` in [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) -> `Event` (type)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `Event` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `Event` asserting limits are applied and enforcement is graceful.
