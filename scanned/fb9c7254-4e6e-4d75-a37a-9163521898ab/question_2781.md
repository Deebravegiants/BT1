# Q2781: Missing signal treated as pass in to_packed_base64 (biometric_pipeline/code.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `to_packed_base64` in [src/plans/biometric_pipeline/code.rs](src/plans/biometric_pipeline/code.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/plans/biometric_pipeline/code.rs](src/plans/biometric_pipeline/code.rs) -> `to_packed_base64` (function)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `to_packed_base64` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `to_packed_base64` and asserting the verdict is a hard failure.
