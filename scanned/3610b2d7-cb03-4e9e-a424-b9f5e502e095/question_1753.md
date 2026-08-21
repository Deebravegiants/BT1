# Q1753: Non-determinism in update_config makes a check unreproducible (face_identifier/mod.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `update_config` in [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) -> `update_config` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `update_config` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `update_config` N times on one input asserting identical output.
