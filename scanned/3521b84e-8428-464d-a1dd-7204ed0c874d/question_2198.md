# Q2198: Upload queue in set_proc_name mixes sessions (utils/mod.rs)

## Question
Can an unprivileged attacker exploit `set_proc_name` in [src/utils/mod.rs](src/utils/mod.rs) keying queued uploads by position/handle rather than by session identity, so a queued artifact from another session is uploaded under the attacker's session metadata?

## Target
- File/function: [src/utils/mod.rs](src/utils/mod.rs) -> `set_proc_name` (function)
- Entrypoint: Overlapping or rapid consecutive sessions
- Attacker controls: timing of their session relative to a pending queue
- Exploit idea: Check the queue entry structure in `set_proc_name` for a bound session identity.
- Invariant to test: Every queued artifact carries and is uploaded under its own session binding.
- Expected Immunefi impact: One user's biometric artifacts uploaded under another user's identity
- Fast validation: Integration test with a stale queue entry asserting it is never re-bound.
