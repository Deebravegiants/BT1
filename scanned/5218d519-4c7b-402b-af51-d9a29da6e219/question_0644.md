# Q0644: Threshold comparison in estimate_once is fail-open (python/rgb_net.rs)

## Question
Can an unprivileged attacker produce a scene where the score compared in `estimate_once` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) is NaN, infinite, or absent, so the comparison evaluates permissively and the check registers as passed?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `estimate_once` (function)
- Entrypoint: Scene conditions producing degenerate model output
- Attacker controls: illumination, occlusion, distance and motion, chosen to push the model to degenerate output
- Exploit idea: Trace the comparison in `estimate_once`: a NaN operand makes `>` and `<` both false, which may select the accept branch.
- Invariant to test: Non-finite or missing scores are rejected explicitly before any comparison.
- Expected Immunefi impact: Fraud/quality check bypassed by degenerate model output
- Fast validation: Unit-test `estimate_once` with NaN/±inf/None scores and assert rejection on every one.
