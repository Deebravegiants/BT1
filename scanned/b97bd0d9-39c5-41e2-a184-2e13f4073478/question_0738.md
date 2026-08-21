# Q0738: Secret material lifetime in monitor_token (short_lived_token.rs)

## Question
Can an unprivileged attacker exploit `monitor_token` in [src/short_lived_token.rs](src/short_lived_token.rs) leaving key/token/plaintext biometric material in memory buffers, temp files, or clones beyond its needed lifetime, so it survives into artifacts (crash dumps, debug reports, uploads) reachable through normal flows?

## Target
- File/function: [src/short_lived_token.rs](src/short_lived_token.rs) -> `monitor_token` (function)
- Entrypoint: Triggering the artifact-producing path (error report, upload, debug capture) during a signup
- Attacker controls: conditions that trigger artifact generation
- Exploit idea: Check `monitor_token` for zeroization and for copies escaping into long-lived structures.
- Invariant to test: Secret and biometric buffers are zeroized and never copied into artifact-producing structures.
- Expected Immunefi impact: Disclosure of keys or raw biometric material via routine artifacts
- Fast validation: Test asserting buffers handled by `monitor_token` are zeroized and absent from generated artifacts.
