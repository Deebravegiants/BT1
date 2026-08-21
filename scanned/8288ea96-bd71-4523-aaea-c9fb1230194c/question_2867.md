# Q2867: Threshold comparison in Agent is fail-open (agents/ir_auto_exposure.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `Agent` in [src/agents/ir_auto_exposure.rs](src/agents/ir_auto_exposure.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [src/agents/ir_auto_exposure.rs](src/agents/ir_auto_exposure.rs) -> `Agent` (type)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `Agent`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `Agent` with NaN/±inf/None scores and assert rejection on every one.
