# Q0729: Secret material lifetime in get_orb_token (identification.rs)

## Question
Can an unprivileged attacker exploit `get_orb_token` in [src/identification.rs](src/identification.rs) leaving key/token/plaintext biometric material in memory buffers, temp files, or clones beyond its needed lifetime, so it survives into artifacts (crash dumps, debug reports, uploads) reachable through normal flows?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `get_orb_token` (function)
- Entrypoint: Triggering the artifact-producing path (error report, upload, debug capture) during a signup
- Attacker controls: conditions that trigger artifact generation
- Exploit idea: Check `get_orb_token` for zeroization and for copies escaping into long-lived structures.
- Invariant to test: Secret and biometric buffers are zeroized and never copied into artifact-producing structures.
- Expected Immunefi impact: Disclosure of keys or raw biometric material via routine artifacts
- Fast validation: Test asserting buffers handled by `get_orb_token` are zeroized and absent from generated artifacts.
