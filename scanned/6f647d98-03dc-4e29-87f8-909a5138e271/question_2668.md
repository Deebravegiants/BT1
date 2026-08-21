# Q2668: Capture-count/quality quota gamed in into_capture (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `into_capture` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `into_capture` (function)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `into_capture` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `into_capture` with N duplicate frames asserting the quota is not met.
