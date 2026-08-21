# Q2772: Version/model mismatch unchecked in set_timeout (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker benefit from `set_timeout` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) not verifying that the model/pipeline version producing a result matches the version the consuming check expects, so scores are interpreted on the wrong scale?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `set_timeout` (function)
- Entrypoint: Any signup executed while a version skew exists
- Attacker controls: timing of the signup relative to component versions in use
- Exploit idea: Check `set_timeout` for a version guard between producer and consumer of the score.
- Invariant to test: Scores carry and enforce a version tag matching the interpreting check.
- Expected Immunefi impact: Fraud/quality thresholds silently misapplied, admitting rejectable captures
- Fast validation: Unit-test `set_timeout` with a mismatched version tag asserting a hard error.
