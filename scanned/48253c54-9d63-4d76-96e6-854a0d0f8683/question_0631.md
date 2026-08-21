# Q0631: Non-determinism in new makes a check unreproducible (python/rgb_net.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `new` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `new` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `new` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `new` N times on one input asserting identical output.
