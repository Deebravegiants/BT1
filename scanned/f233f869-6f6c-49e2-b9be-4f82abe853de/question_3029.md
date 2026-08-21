# Q3029: Version/model mismatch unchecked in version (rgb-net/lib.rs)

## Question
Can an unprivileged attacker benefit from `version` in [rgb-net/src/lib.rs](rgb-net/src/lib.rs) not verifying that the model/pipeline version producing a result matches the version the consuming check expects, so scores are interpreted on the wrong scale?

## Target
- File/function: [rgb-net/src/lib.rs](rgb-net/src/lib.rs) -> `version` (function)
- Entrypoint: Any signup executed while a version skew exists
- Attacker controls: timing of the signup relative to component versions in use
- Exploit idea: Check `version` for a version guard between producer and consumer of the score.
- Invariant to test: Scores carry and enforce a version tag matching the interpreting check.
- Expected Immunefi impact: Fraud/quality thresholds silently misapplied, admitting rejectable captures
- Fast validation: Unit-test `version` with a mismatched version tag asserting a hard error.
