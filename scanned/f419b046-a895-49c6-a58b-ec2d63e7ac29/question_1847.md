# Q1847: Unbounded buffering of inference inputs in from_py_err (ai-interface/lib.rs)

## Question
Can an unprivileged attacker sustain a scene that makes `from_py_err` in [ai-interface/src/lib.rs](ai-interface/src/lib.rs) enqueue inference inputs faster than they drain, growing memory without bound until the signup process is killed and the session's state is left inconsistent?

## Target
- File/function: [ai-interface/src/lib.rs](ai-interface/src/lib.rs) -> `from_py_err` (function)
- Entrypoint: Scene sustaining maximum detection/inference load
- Attacker controls: scene complexity and duration
- Exploit idea: Check `from_py_err` for a bounded channel/backpressure policy versus unbounded queuing.
- Invariant to test: All inference queues are bounded with a defined, safe drop/abort policy.
- Expected Immunefi impact: Attacker-induced OOM leaving the Orb in an inconsistent signup state
- Fast validation: Load test on `from_py_err` asserting bounded queue depth under saturation.
