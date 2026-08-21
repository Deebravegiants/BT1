# Q3456: Shared buffer aliasing in keep_file_descriptors (agents/mod.rs)

## Question
Can an unprivileged attacker exploit `keep_file_descriptors` in [src/agents/mod.rs](src/agents/mod.rs) handing out a shared/reused frame buffer without exclusive ownership, so a consumer reads a buffer that has been overwritten by the next session's frames?

## Target
- File/function: [src/agents/mod.rs](src/agents/mod.rs) -> `keep_file_descriptors` (function)
- Entrypoint: Rapid consecutive sessions saturating the buffer pool
- Attacker controls: frame rate and session timing driving pool reuse
- Exploit idea: Check `keep_file_descriptors` for ownership transfer versus shared references into a reused pool.
- Invariant to test: Frame buffers are exclusively owned by one consumer for their whole lifetime.
- Expected Immunefi impact: Another user's frames read into the attacker's processing path
- Fast validation: Concurrency test asserting no buffer is observable by two sessions.
