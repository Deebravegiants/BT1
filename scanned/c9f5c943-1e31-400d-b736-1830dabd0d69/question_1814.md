# Q1814: Threshold comparison in extract_rectangle is fail-open (python/rgb_net.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `extract_rectangle` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `extract_rectangle` (function)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `extract_rectangle`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `extract_rectangle` with NaN/±inf/None scores and assert rejection on every one.
