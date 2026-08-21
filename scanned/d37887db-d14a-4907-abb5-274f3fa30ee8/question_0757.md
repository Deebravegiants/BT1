# Q0757: Identity value trusted from an unauthenticated source in handle_get_sharpest_frame (agents/image_notary.rs)

## Question
Can an unprivileged attacker influence the identity value that `handle_get_sharpest_frame` in [src/agents/image_notary.rs](src/agents/image_notary.rs) reads (orb id, user id, session id, token) via an unauthenticated source (env var, file, scanned payload, cached value), so the package is filed under an identity not their own?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `handle_get_sharpest_frame` (function)
- Entrypoint: Whichever of those sources is reachable without privilege — in particular scanned payload fields
- Attacker controls: the identity string entering the function
- Exploit idea: Trace each identity input of `handle_get_sharpest_frame` to its origin and its authenticity guarantee.
- Invariant to test: Identity values used in attestation come only from authenticated, device-bound sources.
- Expected Immunefi impact: Biometric record attributed to another user or another Orb
- Fast validation: Unit-test `handle_get_sharpest_frame` with an attacker-shaped identity input asserting rejection.
