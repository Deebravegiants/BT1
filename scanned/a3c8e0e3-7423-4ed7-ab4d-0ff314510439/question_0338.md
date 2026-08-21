# Q0338: Non-determinism in CaptureFailureFeedbackMessage makes a check unreproducible (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker exploit non-determinism in `CaptureFailureFeedbackMessage` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) (thread ordering, uninitialized reuse, floating-point path) so repeated attempts on identical input produce different verdicts, and retry until the favourable one occurs?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `CaptureFailureFeedbackMessage` (type)
- Entrypoint: Repeated identical presentations
- Attacker controls: repetition count on identical physical input
- Exploit idea: Check `CaptureFailureFeedbackMessage` for order-dependent or reuse-dependent computation of the verdict.
- Invariant to test: Identical input yields an identical verdict, every time.
- Expected Immunefi impact: Anti-fraud verdict brute-forced through non-determinism
- Fast validation: Determinism test running `CaptureFailureFeedbackMessage` N times on one input asserting identical output.
