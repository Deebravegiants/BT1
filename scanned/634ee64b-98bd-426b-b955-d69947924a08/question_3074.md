# Q3074: Secret material lifetime in read_versions_json (identification.rs)

## Question
Can an unprivileged attacker exploit `read_versions_json` in [src/identification.rs](src/identification.rs) leaving key/token/plaintext biometric material in memory buffers, temp files, or clones beyond its needed lifetime, so it survives into artifacts (crash dumps, debug reports, uploads) reachable through normal flows?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `read_versions_json` (function)
- Entrypoint: Triggering the artifact-producing path (error report, upload, debug capture) during a signup
- Attacker controls: conditions that trigger artifact generation
- Exploit idea: Check `read_versions_json` for zeroization and for copies escaping into long-lived structures.
- Invariant to test: Secret and biometric buffers are zeroized and never copied into artifact-producing structures.
- Expected Immunefi impact: Disclosure of keys or raw biometric material via routine artifacts
- Fast validation: Test asserting buffers handled by `read_versions_json` are zeroized and absent from generated artifacts.
