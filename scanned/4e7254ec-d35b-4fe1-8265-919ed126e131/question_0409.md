# Q0409: Missing signal treated as pass in poll_extra (biometric_capture/pupil_contraction.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `poll_extra` in [src/plans/biometric_capture/pupil_contraction.rs](src/plans/biometric_capture/pupil_contraction.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/plans/biometric_capture/pupil_contraction.rs](src/plans/biometric_capture/pupil_contraction.rs) -> `poll_extra` (function)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `poll_extra` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `poll_extra` and asserting the verdict is a hard failure.
