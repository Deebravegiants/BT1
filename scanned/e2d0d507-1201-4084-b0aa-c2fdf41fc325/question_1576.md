# Q1576: Non-determinism in Plan makes a check unreproducible (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `Plan` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `Plan` (type)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `Plan` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `Plan` N times on one input asserting identical output.
