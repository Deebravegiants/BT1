# Q3393: Resource limits on the child process in is_terminated (agentwire/port.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `is_terminated` in [agentwire/src/port.rs](agentwire/src/port.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `is_terminated` (function)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `is_terminated` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `is_terminated` asserting limits are applied and enforcement is graceful.
