# Q1619: Threshold comparison in fraud_detected is fail-open (plans/fraud_check.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `fraud_detected` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `fraud_detected` (function)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `fraud_detected`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `fraud_detected` with NaN/±inf/None scores and assert rejection on every one.
