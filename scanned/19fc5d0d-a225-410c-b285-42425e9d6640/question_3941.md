# Q3941: Non-determinism in run_occlusion makes a check unreproducible (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `run_occlusion` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `run_occlusion` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `run_occlusion` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `run_occlusion` N times on one input asserting identical output.
