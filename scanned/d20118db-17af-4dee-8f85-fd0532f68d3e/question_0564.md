# Q0564: Version/model mismatch unchecked in serialized_image_and_mask (iris/types.rs)

## Question
Can an unprivileged attacker benefit from `serialized_image_and_mask` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) not verifying that the model/pipeline version producing a result matches the version the consuming check expects, so scores are interpreted on the wrong scale?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `serialized_image_and_mask` (function)
- Entrypoint: Any signup executed while a version skew exists
- Attacker controls: timing of the signup relative to component versions in use
- Exploit idea: Check `serialized_image_and_mask` for a version guard between producer and consumer of the score.
- Invariant to test: Scores carry and enforce a version tag matching the interpreting check.
- Expected Immunefi impact: Fraud/quality thresholds silently misapplied, admitting rejectable captures
- Fast validation: Unit-test `serialized_image_and_mask` with a mismatched version tag asserting a hard error.
