# Q2935: Unbounded buffering of inference inputs in Bundle (face_identifier/types.rs)

## Question
Can an unprivileged attacker sustain a scene that makes `Bundle` in [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) enqueue inference inputs faster than they drain, growing memory without bound until the signup process is killed and the session's state is left inconsistent?

## Target
- File/function: [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) -> `Bundle` (type)
- Entrypoint: Scene sustaining maximum detection/inference load
- Attacker controls: scene complexity and duration
- Exploit idea: Check `Bundle` for a bounded channel/backpressure policy versus unbounded queuing.
- Invariant to test: All inference queues are bounded with a defined, safe drop/abort policy.
- Expected Immunefi impact: Attacker-induced OOM leaving the Orb in an inconsistent signup state
- Fast validation: Load test on `Bundle` asserting bounded queue depth under saturation.
