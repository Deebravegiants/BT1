# Q2984: Version/model mismatch unchecked in is_correct (python/rgb_net.rs)

## Question
Can an unprivileged attacker benefit from `is_correct` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) not verifying that the model/pipeline version producing a result matches the version the consuming check expects, so scores are interpreted on the wrong scale?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `is_correct` (function)
- Entrypoint: Any signup executed while a version skew exists
- Attacker controls: timing of the signup relative to component versions in use
- Exploit idea: Check `is_correct` for a version guard between producer and consumer of the score.
- Invariant to test: Scores carry and enforce a version tag matching the interpreting check.
- Expected Immunefi impact: Fraud/quality thresholds silently misapplied, admitting rejectable captures
- Fast validation: Unit-test `is_correct` with a mismatched version tag asserting a hard error.
