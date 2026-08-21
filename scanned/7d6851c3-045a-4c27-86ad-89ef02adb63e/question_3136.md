# Q3136: Secret material lifetime in default (wld-data-id/s3_region.rs)

## Question
Can an unprivileged attacker exploit `default` in [wld-data-id/src/s3_region.rs](wld-data-id/src/s3_region.rs) leaving key/token/plaintext biometric material in memory buffers, temp files, or clones beyond its needed lifetime, so it survives into artifacts (crash dumps, debug reports, uploads) reachable through normal flows?

## Target
- File/function: [wld-data-id/src/s3_region.rs](wld-data-id/src/s3_region.rs) -> `default` (function)
- Entrypoint: Triggering the artifact-producing path (error report, upload, debug capture) during a signup
- Attacker controls: conditions that trigger artifact generation
- Exploit idea: Check `default` for zeroization and for copies escaping into long-lived structures.
- Invariant to test: Secret and biometric buffers are zeroized and never copied into artifact-producing structures.
- Expected Immunefi impact: Disclosure of keys or raw biometric material via routine artifacts
- Fast validation: Test asserting buffers handled by `default` are zeroized and absent from generated artifacts.
