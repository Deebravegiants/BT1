# Q0174: Resource limits on the child process in init_dbus (brokers/orb.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `init_dbus` in [src/brokers/orb.rs](src/brokers/orb.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `init_dbus` (function)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `init_dbus` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `init_dbus` asserting limits are applied and enforcement is graceful.
