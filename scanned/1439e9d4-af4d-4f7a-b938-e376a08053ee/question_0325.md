# Q0325: Capture-count/quality quota gamed in set_next_objective (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `set_next_objective` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `set_next_objective` (function)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `set_next_objective` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `set_next_objective` with N duplicate frames asserting the quota is not met.
