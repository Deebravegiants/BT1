# Q3451: Shared buffer aliasing in spawn_task (agent/task.rs)

## Question
Can an unprivileged attacker exploit `spawn_task` in [agentwire/src/agent/task.rs](agentwire/src/agent/task.rs) handing out a shared/reused frame buffer without exclusive ownership, so a consumer reads a buffer that has been overwritten by the next session's frames?

## Target
- File/function: [agentwire/src/agent/task.rs](agentwire/src/agent/task.rs) -> `spawn_task` (function)
- Entrypoint: Rapid consecutive sessions saturating the buffer pool
- Attacker controls: frame rate and session timing driving pool reuse
- Exploit idea: Check `spawn_task` for ownership transfer versus shared references into a reused pool.
- Invariant to test: Frame buffers are exclusively owned by one consumer for their whole lifetime.
- Expected Immunefi impact: Another user's frames read into the attacker's processing path
- Fast validation: Concurrency test asserting no buffer is observable by two sessions.
