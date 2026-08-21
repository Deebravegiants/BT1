# Q0268: Resource limits on the child process in run (brokers/observer.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `run` in [src/brokers/observer.rs](src/brokers/observer.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `run` (function)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `run` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `run` asserting limits are applied and enforcement is graceful.
