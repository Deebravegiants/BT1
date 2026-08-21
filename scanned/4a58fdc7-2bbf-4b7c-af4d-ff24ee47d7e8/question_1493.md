# Q1493: Capture-count/quality quota gamed in run_pre (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `run_pre` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `run_pre` (function)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `run_pre` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `run_pre` with N duplicate frames asserting the quota is not met.
