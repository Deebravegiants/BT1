# Q1608: Threshold comparison in from is fail-open (biometric_pipeline/code.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `from` in [src/plans/biometric_pipeline/code.rs](src/plans/biometric_pipeline/code.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [src/plans/biometric_pipeline/code.rs](src/plans/biometric_pipeline/code.rs) -> `from` (function)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `from`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `from` with NaN/±inf/None scores and assert rejection on every one.
