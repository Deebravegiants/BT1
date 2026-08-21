# Q0696: Secret material lifetime in make_face_embeddings_json (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker exploit `make_face_embeddings_json` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) leaving key/token/plaintext biometric material in memory buffers, temp files, or clones beyond its needed lifetime, so it survives into artifacts (crash dumps, debug reports, uploads) reachable through normal flows?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_face_embeddings_json` (function)
- Entrypoint: Triggering the artifact-producing path (error report, upload, debug capture) during a signup
- Attacker controls: conditions that trigger artifact generation
- Exploit idea: Check `make_face_embeddings_json` for zeroization and for copies escaping into long-lived structures.
- Invariant to test: Secret and biometric buffers are zeroized and never copied into artifact-producing structures.
- Expected Immunefi impact: Disclosure of keys or raw biometric material via routine artifacts
- Fast validation: Test asserting buffers handled by `make_face_embeddings_json` are zeroized and absent from generated artifacts.
