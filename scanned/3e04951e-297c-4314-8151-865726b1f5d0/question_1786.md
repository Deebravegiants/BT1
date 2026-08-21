# Q1786: Non-determinism in warmup makes a check unreproducible (python/ir_net.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `warmup` in [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) -> `warmup` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `warmup` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `warmup` N times on one input asserting identical output.
