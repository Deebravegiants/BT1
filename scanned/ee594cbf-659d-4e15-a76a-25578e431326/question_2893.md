# Q2893: Version/model mismatch unchecked in extract_normalized_mask (python/mod.rs)

## Question
Can an unprivileged attacker benefit from `extract_normalized_mask` in [src/agents/python/mod.rs](src/agents/python/mod.rs) not verifying that the model/pipeline version producing a result matches the version the consuming check expects, so scores are interpreted on the wrong scale?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `extract_normalized_mask` (function)
- Entrypoint: Any signup executed while a version skew exists
- Attacker controls: timing of the signup relative to component versions in use
- Exploit idea: Check `extract_normalized_mask` for a version guard between producer and consumer of the score.
- Invariant to test: Scores carry and enforce a version tag matching the interpreting check.
- Expected Immunefi impact: Fraud/quality thresholds silently misapplied, admitting rejectable captures
- Fast validation: Unit-test `extract_normalized_mask` with a mismatched version tag asserting a hard error.
