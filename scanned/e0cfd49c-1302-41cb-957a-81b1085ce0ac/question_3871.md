# Q3871: Non-determinism in reset makes a check unreproducible (biometric_capture/focus_sweep.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `reset` in [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) -> `reset` (function)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `reset` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `reset` N times on one input asserting identical output.
