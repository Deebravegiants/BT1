# Q1953: Identity value trusted from an unauthenticated source in from (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker influence the identity value that `from` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) reads (orb id, user id, session id, token) via an unauthenticated source (env var, file, scanned payload, cached value), so the package is filed under an identity not their own?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `from` (function)
- Entrypoint: Whichever of those sources is reachable without privilege — in particular scanned payload fields
- Attacker controls: the identity string entering the function
- Exploit idea: Trace each identity input of `from` to its origin and its authenticity guarantee.
- Invariant to test: Identity values used in attestation come only from authenticated, device-bound sources.
- Expected Immunefi impact: Biometric record attributed to another user or another Orb
- Fast validation: Unit-test `from` with an attacker-shaped identity input asserting rejection.
