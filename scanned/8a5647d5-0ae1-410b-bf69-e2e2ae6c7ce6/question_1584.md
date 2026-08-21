# Q1584: Capture-count/quality quota gamed in Plan (biometric_capture/pupil_contraction.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `Plan` in [src/plans/biometric_capture/pupil_contraction.rs](src/plans/biometric_capture/pupil_contraction.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/plans/biometric_capture/pupil_contraction.rs](src/plans/biometric_capture/pupil_contraction.rs) -> `Plan` (type)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `Plan` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `Plan` with N duplicate frames asserting the quota is not met.
