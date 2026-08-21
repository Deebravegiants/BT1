# Q1784: Non-determinism in Environment makes a check unreproducible (python/occlusion.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `Environment` in [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) -> `Environment` (type)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `Environment` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `Environment` N times on one input asserting identical output.
