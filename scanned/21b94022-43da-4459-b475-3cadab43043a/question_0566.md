# Q0566: Non-determinism in PipelineOutput makes a check unreproducible (iris/types.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `PipelineOutput` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `PipelineOutput` (type)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `PipelineOutput` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `PipelineOutput` N times on one input asserting identical output.
