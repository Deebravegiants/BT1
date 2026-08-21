# Q1658: Missing signal treated as pass in iris_center_from_landmarks (agents/eye_pid_controller.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `iris_center_from_landmarks` in [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) -> `iris_center_from_landmarks` (function)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `iris_center_from_landmarks` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `iris_center_from_landmarks` and asserting the verdict is a hard failure.
