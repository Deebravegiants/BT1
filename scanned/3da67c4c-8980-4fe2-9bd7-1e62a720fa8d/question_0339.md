# Q0339: Unbounded buffering of inference inputs in Output (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker sustain a scene that makes `Output` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) enqueue inference inputs faster than they drain, growing memory without bound until the signup process is killed and the session's state is left inconsistent?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `Output` (type)
- Entrypoint: Scene sustaining maximum detection/inference load
- Attacker controls: scene complexity and duration
- Exploit idea: Check `Output` for a bounded channel/backpressure policy versus unbounded queuing.
- Invariant to test: All inference queues are bounded with a defined, safe drop/abort policy.
- Expected Immunefi impact: Attacker-induced OOM leaving the Orb in an inconsistent signup state
- Fast validation: Load test on `Output` asserting bounded queue depth under saturation.
