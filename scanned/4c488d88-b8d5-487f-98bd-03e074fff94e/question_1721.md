# Q1721: Unbounded buffering of inference inputs in extract_normalized_mask (python/mod.rs)

## Question
Can an unprivileged attacker sustain a scene that makes `extract_normalized_mask` in [src/agents/python/mod.rs](src/agents/python/mod.rs) enqueue inference inputs faster than they drain, growing memory without bound until the signup process is killed and the session's state is left inconsistent?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `extract_normalized_mask` (function)
- Entrypoint: Scene sustaining maximum detection/inference load
- Attacker controls: scene complexity and duration
- Exploit idea: Check `extract_normalized_mask` for a bounded channel/backpressure policy versus unbounded queuing.
- Invariant to test: All inference queues are bounded with a defined, safe drop/abort policy.
- Expected Immunefi impact: Attacker-induced OOM leaving the Orb in an inconsistent signup state
- Fast validation: Load test on `extract_normalized_mask` asserting bounded queue depth under saturation.
