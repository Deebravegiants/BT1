# Q0402: Missing signal treated as pass in parse_duration (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `parse_duration` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `parse_duration` (function)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `parse_duration` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `parse_duration` and asserting the verdict is a hard failure.
