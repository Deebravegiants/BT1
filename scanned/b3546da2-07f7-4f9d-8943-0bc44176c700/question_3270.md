# Q3270: Upload queue in biometric_capture_feedback_messages mixes sessions (debug_report.rs)

## Question
Can an unprivileged attacker exploit `biometric_capture_feedback_messages` in [src/debug_report.rs](src/debug_report.rs) keying queued uploads by position/handle rather than by session identity, so a queued artifact from another session is uploaded under the attacker's session metadata?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `biometric_capture_feedback_messages` (function)
- Entrypoint: Overlapping or rapid consecutive sessions
- Attacker controls: timing of their session relative to a pending queue
- Exploit idea: Check the queue entry structure in `biometric_capture_feedback_messages` for a bound session identity.
- Invariant to test: Every queued artifact carries and is uploaded under its own session binding.
- Expected Immunefi impact: One user's biometric artifacts uploaded under another user's identity
- Fast validation: Integration test with a stale queue entry asserting it is never re-bound.
