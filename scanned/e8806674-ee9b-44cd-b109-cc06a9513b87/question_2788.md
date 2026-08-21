# Q2788: Missing signal treated as pass in enabled_checks_from_config (plans/fraud_check.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `enabled_checks_from_config` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `enabled_checks_from_config` (function)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `enabled_checks_from_config` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `enabled_checks_from_config` and asserting the verdict is a hard failure.
