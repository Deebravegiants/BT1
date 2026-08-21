# Q1148: Shared buffer aliasing in get_buffered_messages (orb-relay-client/client.rs)

## Question
Can an unprivileged attacker exploit `get_buffered_messages` in [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) handing out a shared/reused frame buffer without exclusive ownership, so a consumer reads a buffer that has been overwritten by the next session's frames?

## Target
- File/function: [orb-relay-client/src/client.rs](orb-relay-client/src/client.rs) -> `get_buffered_messages` (function)
- Entrypoint: Rapid consecutive sessions saturating the buffer pool
- Attacker controls: frame rate and session timing driving pool reuse
- Exploit idea: Check `get_buffered_messages` for ownership transfer versus shared references into a reused pool.
- Invariant to test: Frame buffers are exclusively owned by one consumer for their whole lifetime.
- Expected Immunefi impact: Another user's frames read into the attacker's processing path
- Fast validation: Concurrency test asserting no buffer is observable by two sessions.
