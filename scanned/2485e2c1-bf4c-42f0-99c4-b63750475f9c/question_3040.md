# Q3040: Identity value trusted from an unauthenticated source in make_face_embeddings_json (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker influence the identity value that `make_face_embeddings_json` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) reads (orb id, user id, session id, token) via an unauthenticated source (env var, file, scanned payload, cached value), so the package is filed under an identity not their own?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_face_embeddings_json` (function)
- Entrypoint: Whichever of those sources is reachable without privilege — in particular scanned payload fields
- Attacker controls: the identity string entering the function
- Exploit idea: Trace each identity input of `make_face_embeddings_json` to its origin and its authenticity guarantee.
- Invariant to test: Identity values used in attestation come only from authenticated, device-bound sources.
- Expected Immunefi impact: Biometric record attributed to another user or another Orb
- Fast validation: Unit-test `make_face_embeddings_json` with an attacker-shaped identity input asserting rejection.
