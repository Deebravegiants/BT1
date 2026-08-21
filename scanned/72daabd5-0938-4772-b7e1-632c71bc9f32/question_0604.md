# Q0604: Non-determinism in occlusion_estimate makes a check unreproducible (python/occlusion.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `occlusion_estimate` in [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) -> `occlusion_estimate` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `occlusion_estimate` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `occlusion_estimate` N times on one input asserting identical output.
