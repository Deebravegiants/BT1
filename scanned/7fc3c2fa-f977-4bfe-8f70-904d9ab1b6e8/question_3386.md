# Q3386: Resource limits on the child process in new (agentwire/port.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `new` in [agentwire/src/port.rs](agentwire/src/port.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `new` (function)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `new` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `new` asserting limits are applied and enforcement is graceful.
