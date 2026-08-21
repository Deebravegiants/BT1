# Q0437: Threshold comparison in to_packed_base64 is fail-open (biometric_pipeline/code.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `to_packed_base64` in [src/plans/biometric_pipeline/code.rs](src/plans/biometric_pipeline/code.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [src/plans/biometric_pipeline/code.rs](src/plans/biometric_pipeline/code.rs) -> `to_packed_base64` (function)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `to_packed_base64`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `to_packed_base64` with NaN/±inf/None scores and assert rejection on every one.
