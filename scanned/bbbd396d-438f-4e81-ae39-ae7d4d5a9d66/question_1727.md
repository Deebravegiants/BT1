# Q1727: Unbounded buffering of inference inputs in initializer (iris/mod.rs)

## Question
Can an unprivileged attacker sustain a scene that makes `initializer` in [src/agents/python/iris/mod.rs](src/agents/python/iris/mod.rs) enqueue inference inputs faster than they drain, growing memory without bound until the signup process is killed and the session's state is left inconsistent?

## Target
- File/function: [src/agents/python/iris/mod.rs](src/agents/python/iris/mod.rs) -> `initializer` (function)
- Entrypoint: Scene sustaining maximum detection/inference load
- Attacker controls: scene complexity and duration
- Exploit idea: Check `initializer` for a bounded channel/backpressure policy versus unbounded queuing.
- Invariant to test: All inference queues are bounded with a defined, safe drop/abort policy.
- Expected Immunefi impact: Attacker-induced OOM leaving the Orb in an inconsistent signup state
- Fast validation: Load test on `initializer` asserting bounded queue depth under saturation.
