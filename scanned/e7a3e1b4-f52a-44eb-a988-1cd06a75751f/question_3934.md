# Q3934: Capture-count/quality quota gamed in handle_face_identifier (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `handle_face_identifier` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `handle_face_identifier` (function)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `handle_face_identifier` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `handle_face_identifier` with N duplicate frames asserting the quota is not met.
