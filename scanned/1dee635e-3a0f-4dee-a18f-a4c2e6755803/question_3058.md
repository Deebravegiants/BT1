# Q3058: Identity value trusted from an unauthenticated source in FaceEmbeddingsJson (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker influence the identity value that `FaceEmbeddingsJson` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) reads (orb id, user id, session id, token) via an unauthenticated source (env var, file, scanned payload, cached value), so the package is filed under an identity not their own?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `FaceEmbeddingsJson` (type)
- Entrypoint: Whichever of those sources is reachable without privilege — in particular scanned payload fields
- Attacker controls: the identity string entering the function
- Exploit idea: Trace each identity input of `FaceEmbeddingsJson` to its origin and its authenticity guarantee.
- Invariant to test: Identity values used in attestation come only from authenticated, device-bound sources.
- Expected Immunefi impact: Biometric record attributed to another user or another Orb
- Fast validation: Unit-test `FaceEmbeddingsJson` with an attacker-shaped identity input asserting rejection.
