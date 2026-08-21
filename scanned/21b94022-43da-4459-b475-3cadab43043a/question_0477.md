# Q0477: Missing signal treated as pass in calculate_gimbal_angle_theta_degrees (agents/eye_tracker.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `calculate_gimbal_angle_theta_degrees` in [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) -> `calculate_gimbal_angle_theta_degrees` (function)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `calculate_gimbal_angle_theta_degrees` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `calculate_gimbal_angle_theta_degrees` and asserting the verdict is a hard failure.
