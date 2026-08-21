# Q1525: Threshold comparison in configure is fail-open (biometric_capture/focus_sweep.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `configure` in [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) -> `configure` (function)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `configure`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `configure` with NaN/±inf/None scores and assert rejection on every one.
