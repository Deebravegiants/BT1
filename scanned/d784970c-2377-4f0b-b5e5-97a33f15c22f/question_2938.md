# Q2938: Version/model mismatch unchecked in BBox (face_identifier/types.rs)

## Question
Can an unprivileged attacker benefit from `BBox` in [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) not verifying that the model/pipeline version producing a result matches the version the consuming check expects, so scores are interpreted on the wrong scale?

## Target
- File/function: [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) -> `BBox` (type)
- Entrypoint: Any signup executed while a version skew exists
- Attacker controls: timing of the signup relative to component versions in use
- Exploit idea: Check `BBox` for a version guard between producer and consumer of the score.
- Invariant to test: Scores carry and enforce a version tag matching the interpreting check.
- Expected Immunefi impact: Fraud/quality thresholds silently misapplied, admitting rejectable captures
- Fast validation: Unit-test `BBox` with a mismatched version tag asserting a hard error.
