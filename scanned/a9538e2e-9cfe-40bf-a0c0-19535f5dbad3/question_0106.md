# Q0106: Resource limits on the child process in has_biometric_input (plans/mod.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `has_biometric_input` in [src/plans/mod.rs](src/plans/mod.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `has_biometric_input` (function)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `has_biometric_input` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `has_biometric_input` asserting limits are applied and enforcement is graceful.
