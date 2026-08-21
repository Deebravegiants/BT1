# Q1630: Threshold comparison in evaluate is fail-open (fraud-engine/dsl.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `evaluate` in [fraud-engine/src/dsl.rs](fraud-engine/src/dsl.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [fraud-engine/src/dsl.rs](fraud-engine/src/dsl.rs) -> `evaluate` (function)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `evaluate`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `evaluate` with NaN/±inf/None scores and assert rejection on every one.
