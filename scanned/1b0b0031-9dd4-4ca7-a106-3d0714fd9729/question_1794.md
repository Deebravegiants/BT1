# Q1794: Unbounded buffering of inference inputs in calculate_selection_score (python/ir_net.rs)

## Question
Can an unprivileged attacker sustain a scene that makes `calculate_selection_score` in [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) enqueue inference inputs faster than they drain, growing memory without bound until the signup process is killed and the session's state is left inconsistent?

## Target
- File/function: [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) -> `calculate_selection_score` (function)
- Entrypoint: Scene sustaining maximum detection/inference load
- Attacker controls: scene complexity and duration
- Exploit idea: Check `calculate_selection_score` for a bounded channel/backpressure policy versus unbounded queuing.
- Invariant to test: All inference queues are bounded with a defined, safe drop/abort policy.
- Expected Immunefi impact: Attacker-induced OOM leaving the Orb in an inconsistent signup state
- Fast validation: Load test on `calculate_selection_score` asserting bounded queue depth under saturation.
