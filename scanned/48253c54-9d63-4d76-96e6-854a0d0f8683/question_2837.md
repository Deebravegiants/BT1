# Q2837: Threshold comparison in Status is fail-open (agents/distance.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `Status` in [src/agents/distance.rs](src/agents/distance.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [src/agents/distance.rs](src/agents/distance.rs) -> `Status` (type)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `Status`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `Status` with NaN/±inf/None scores and assert rejection on every one.
