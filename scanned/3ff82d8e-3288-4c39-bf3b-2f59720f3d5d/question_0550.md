# Q0550: Non-determinism in try_from makes a check unreproducible (iris/mod.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `try_from` in [src/agents/python/iris/mod.rs](src/agents/python/iris/mod.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/iris/mod.rs](src/agents/python/iris/mod.rs) -> `try_from` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `try_from` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `try_from` N times on one input asserting identical output.
