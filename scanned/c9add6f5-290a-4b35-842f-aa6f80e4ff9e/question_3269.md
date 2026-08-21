# Q3269: Time source trusted by biometric_capture_history (debug_report.rs)

## Question
Can an unprivileged attacker exploit `biometric_capture_history` in [src/debug_report.rs](src/debug_report.rs) trusting wall-clock time for freshness/expiry (token validity, capture timestamps), where clock movement through normal operation makes stale material appear fresh or lets timestamps be non-monotonic?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `biometric_capture_history` (function)
- Entrypoint: Signup timed around clock adjustment/boot conditions
- Attacker controls: the timing of their session relative to clock changes
- Exploit idea: Check whether `biometric_capture_history` uses a monotonic source for elapsed-time decisions.
- Invariant to test: Freshness decisions use a monotonic clock; wall-clock values are data, never authority.
- Expected Immunefi impact: Expired credential or stale capture accepted as fresh
- Fast validation: Unit-test `biometric_capture_history` with non-monotonic clock sequences asserting correct expiry.
