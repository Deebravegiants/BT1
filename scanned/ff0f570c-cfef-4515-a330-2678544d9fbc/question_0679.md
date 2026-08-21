# Q0679: Non-determinism in init makes a check unreproducible (ir-net/lib.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `init` in [ir-net/src/lib.rs](ir-net/src/lib.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [ir-net/src/lib.rs](ir-net/src/lib.rs) -> `init` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `init` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `init` N times on one input asserting identical output.
