# Q2205: Upload queue in new mixes sessions (utils/serializable_instant.rs)

## Question
Can an unprivileged attacker exploit `new` in [src/utils/serializable_instant.rs](src/utils/serializable_instant.rs) keying queued uploads by position/handle rather than by session identity, so a queued artifact from another session is uploaded under the attacker's session metadata?

## Target
- File/function: [src/utils/serializable_instant.rs](src/utils/serializable_instant.rs) -> `new` (function)
- Entrypoint: Overlapping or rapid consecutive sessions
- Attacker controls: timing of their session relative to a pending queue
- Exploit idea: Check the queue entry structure in `new` for a bound session identity.
- Invariant to test: Every queued artifact carries and is uploaded under its own session binding.
- Expected Immunefi impact: One user's biometric artifacts uploaded under another user's identity
- Fast validation: Integration test with a stale queue entry asserting it is never re-bound.
