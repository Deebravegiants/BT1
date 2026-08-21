# Q1515: Capture-count/quality quota gamed in handle_ir_auto_focus (biometric_capture/focus_sweep.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `handle_ir_auto_focus` in [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) -> `handle_ir_auto_focus` (function)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `handle_ir_auto_focus` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `handle_ir_auto_focus` with N duplicate frames asserting the quota is not met.
