# Q0563: Non-determinism in serialized_mask makes a check unreproducible (iris/types.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `serialized_mask` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `serialized_mask` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `serialized_mask` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `serialized_mask` N times on one input asserting identical output.
