# Q0397: Threshold comparison in reset_extension is fail-open (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `reset_extension` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `reset_extension` (function)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `reset_extension`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `reset_extension` with NaN/±inf/None scores and assert rejection on every one.
