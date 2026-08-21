# Q1009: Upload queue in new_with_keep_fds mixes sessions (process.rs)

## Question
Can an unprivileged attacker exploit `new_with_keep_fds` in [src/process.rs](src/process.rs) keying queued uploads by position/handle rather than by session identity, so a queued artifact from another session is uploaded under the attacker's session metadata?

## Target
- File/function: [src/process.rs](src/process.rs) -> `new_with_keep_fds` (function)
- Entrypoint: Overlapping or rapid consecutive sessions
- Attacker controls: timing of their session relative to a pending queue
- Exploit idea: Check the queue entry structure in `new_with_keep_fds` for a bound session identity.
- Invariant to test: Every queued artifact carries and is uploaded under its own session binding.
- Expected Immunefi impact: One user's biometric artifacts uploaded under another user's identity
- Fast validation: Integration test with a stale queue entry asserting it is never re-bound.
