# Q0921: Identity value trusted from an unauthenticated source in iris_model_error (debug_report.rs)

## Question
Can an unprivileged attacker influence the identity value that `iris_model_error` in [src/debug_report.rs](src/debug_report.rs) reads (orb id, user id, session id, token) via an unauthenticated source (env var, file, scanned payload, cached value), so the package is filed under an identity not their own?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `iris_model_error` (function)
- Entrypoint: Whichever of those sources is reachable without privilege — in particular scanned payload fields
- Attacker controls: the identity string entering the function
- Exploit idea: Trace each identity input of `iris_model_error` to its origin and its authenticity guarantee.
- Invariant to test: Identity values used in attestation come only from authenticated, device-bound sources.
- Expected Immunefi impact: Biometric record attributed to another user or another Orb
- Fast validation: Unit-test `iris_model_error` with an attacker-shaped identity input asserting rejection.
