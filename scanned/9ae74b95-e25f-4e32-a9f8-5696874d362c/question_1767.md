# Q1767: Non-determinism in Point makes a check unreproducible (face_identifier/types.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `Point` in [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) -> `Point` (type)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `Point` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `Point` N times on one input asserting identical output.
