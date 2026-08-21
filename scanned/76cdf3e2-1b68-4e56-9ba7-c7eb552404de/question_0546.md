# Q0546: Unbounded buffering of inference inputs in init_sys_argv (python/mod.rs)

## Question
Can an unprivileged attacker sustain a scene that makes `init_sys_argv` in [src/agents/python/mod.rs](src/agents/python/mod.rs) enqueue inference inputs faster than they drain, growing memory without bound until the signup process is killed and the session's state is left inconsistent?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `init_sys_argv` (function)
- Entrypoint: Scene sustaining maximum detection/inference load
- Attacker controls: scene complexity and duration
- Exploit idea: Check `init_sys_argv` for a bounded channel/backpressure policy versus unbounded queuing.
- Invariant to test: All inference queues are bounded with a defined, safe drop/abort policy.
- Expected Immunefi impact: Attacker-induced OOM leaving the Orb in an inconsistent signup state
- Fast validation: Load test on `init_sys_argv` asserting bounded queue depth under saturation.
