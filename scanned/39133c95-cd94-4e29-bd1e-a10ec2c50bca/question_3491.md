# Q3491: Resource limits on the child process in check_for_msg (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker drive the process spawned/managed by `check_for_msg` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) past its memory/fd/time limits (or observe that no limits exist), so the whole signup runtime is destabilized from routine capture input?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `check_for_msg` (function)
- Entrypoint: Capture load driving the child process
- Attacker controls: scene complexity and duration
- Exploit idea: Check `check_for_msg` for rlimits/cgroups/timeouts on the managed process.
- Invariant to test: Child processes run under explicit resource limits with a defined kill policy.
- Expected Immunefi impact: Attacker-induced runtime destabilization breaking Orb availability persistently
- Fast validation: Load test on `check_for_msg` asserting limits are applied and enforcement is graceful.
