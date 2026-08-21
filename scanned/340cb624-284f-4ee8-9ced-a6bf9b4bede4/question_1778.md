# Q1778: Version/model mismatch unchecked in run (python/occlusion.rs)

## Question
Can an unprivileged attacker benefit from `run` in [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) not verifying that the model/pipeline version producing a result matches the version the consuming check expects, so scores are interpreted on the wrong scale?

## Target
- File/function: [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) -> `run` (function)
- Entrypoint: Any signup executed while a version skew exists
- Attacker controls: timing of the signup relative to component versions in use
- Exploit idea: Check `run` for a version guard between producer and consumer of the score.
- Invariant to test: Scores carry and enforce a version tag matching the interpreting check.
- Expected Immunefi impact: Fraud/quality thresholds silently misapplied, admitting rejectable captures
- Fast validation: Unit-test `run` with a mismatched version tag asserting a hard error.
