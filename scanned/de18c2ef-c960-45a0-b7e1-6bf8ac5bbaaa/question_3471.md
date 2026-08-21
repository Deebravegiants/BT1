# Q3471: Shared buffer aliasing in push (livestream/downstream.rs)

## Question
Can an unprivileged attacker exploit `push` in [src/agents/livestream/downstream.rs](src/agents/livestream/downstream.rs) handing out a shared/reused frame buffer without exclusive ownership, so a consumer reads a buffer that has been overwritten by the next session's frames?

## Target
- File/function: [src/agents/livestream/downstream.rs](src/agents/livestream/downstream.rs) -> `push` (function)
- Entrypoint: Rapid consecutive sessions saturating the buffer pool
- Attacker controls: frame rate and session timing driving pool reuse
- Exploit idea: Check `push` for ownership transfer versus shared references into a reused pool.
- Invariant to test: Frame buffers are exclusively owned by one consumer for their whole lifetime.
- Expected Immunefi impact: Another user's frames read into the attacker's processing path
- Fast validation: Concurrency test asserting no buffer is observable by two sessions.
