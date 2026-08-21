# Q3690: Shared buffer aliasing in init_dbus (brokers/orb.rs)

## Question
Can an unprivileged attacker exploit `init_dbus` in [src/brokers/orb.rs](src/brokers/orb.rs) handing out a shared/reused frame buffer without exclusive ownership, so a consumer reads a buffer that has been overwritten by the next session's frames?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `init_dbus` (function)
- Entrypoint: Rapid consecutive sessions saturating the buffer pool
- Attacker controls: frame rate and session timing driving pool reuse
- Exploit idea: Check `init_dbus` for ownership transfer versus shared references into a reused pool.
- Invariant to test: Frame buffers are exclusively owned by one consumer for their whole lifetime.
- Expected Immunefi impact: Another user's frames read into the attacker's processing path
- Fast validation: Concurrency test asserting no buffer is observable by two sessions.
