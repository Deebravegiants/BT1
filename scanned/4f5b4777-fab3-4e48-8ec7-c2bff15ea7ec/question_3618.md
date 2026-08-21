# Q3618: Shared buffer aliasing in verify_user_qr_code (plans/mod.rs)

## Question
Can an unprivileged attacker exploit `verify_user_qr_code` in [src/plans/mod.rs](src/plans/mod.rs) handing out a shared/reused frame buffer without exclusive ownership, so a consumer reads a buffer that has been overwritten by the next session's frames?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `verify_user_qr_code` (function)
- Entrypoint: Rapid consecutive sessions saturating the buffer pool
- Attacker controls: frame rate and session timing driving pool reuse
- Exploit idea: Check `verify_user_qr_code` for ownership transfer versus shared references into a reused pool.
- Invariant to test: Frame buffers are exclusively owned by one consumer for their whole lifetime.
- Expected Immunefi impact: Another user's frames read into the attacker's processing path
- Fast validation: Concurrency test asserting no buffer is observable by two sessions.
