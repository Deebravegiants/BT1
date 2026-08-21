# Q3261: Secret material lifetime in fraud_check_feedback_messages (debug_report.rs)

## Question
Can an unprivileged attacker exploit `fraud_check_feedback_messages` in [src/debug_report.rs](src/debug_report.rs) leaving key/token/plaintext biometric material in memory buffers, temp files, or clones beyond its needed lifetime, so it survives into artifacts (crash dumps, debug reports, uploads) reachable through normal flows?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `fraud_check_feedback_messages` (function)
- Entrypoint: Triggering the artifact-producing path (error report, upload, debug capture) during a signup
- Attacker controls: conditions that trigger artifact generation
- Exploit idea: Check `fraud_check_feedback_messages` for zeroization and for copies escaping into long-lived structures.
- Invariant to test: Secret and biometric buffers are zeroized and never copied into artifact-producing structures.
- Expected Immunefi impact: Disclosure of keys or raw biometric material via routine artifacts
- Fast validation: Test asserting buffers handled by `fraud_check_feedback_messages` are zeroized and absent from generated artifacts.
