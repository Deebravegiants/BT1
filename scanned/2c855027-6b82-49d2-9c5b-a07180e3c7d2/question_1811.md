# Q1811: Unbounded buffering of inference inputs in is_face_detected (python/rgb_net.rs)

## Question
Can an unprivileged attacker sustain a scene that makes `is_face_detected` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) enqueue inference inputs faster than they drain, growing memory without bound until the signup process is killed and the session's state is left inconsistent?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `is_face_detected` (function)
- Entrypoint: Scene sustaining maximum detection/inference load
- Attacker controls: scene complexity and duration
- Exploit idea: Check `is_face_detected` for a bounded channel/backpressure policy versus unbounded queuing.
- Invariant to test: All inference queues are bounded with a defined, safe drop/abort policy.
- Expected Immunefi impact: Attacker-induced OOM leaving the Orb in an inconsistent signup state
- Fast validation: Load test on `is_face_detected` asserting bounded queue depth under saturation.
