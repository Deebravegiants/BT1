# Q2892: Non-determinism in extract_normalized_iris makes a check unreproducible (python/mod.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `extract_normalized_iris` in [src/agents/python/mod.rs](src/agents/python/mod.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `extract_normalized_iris` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `extract_normalized_iris` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `extract_normalized_iris` N times on one input asserting identical output.
