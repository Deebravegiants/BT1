# Q2931: Threshold comparison in Input is fail-open (face_identifier/mod.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `Input` in [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) -> `Input` (type)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `Input`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `Input` with NaN/±inf/None scores and assert rejection on every one.
