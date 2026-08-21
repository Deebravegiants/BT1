# Q3945: Version/model mismatch unchecked in run_update_all_configs (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker benefit from `run_update_all_configs` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) not verifying that the model/pipeline version producing a result matches the version the consuming check expects, so scores are interpreted on the wrong scale?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `run_update_all_configs` (function)
- Entrypoint: Any signup executed while a version skew exists
- Attacker controls: timing of the signup relative to component versions in use
- Exploit idea: Check `run_update_all_configs` for a version guard between producer and consumer of the score.
- Invariant to test: Scores carry and enforce a version tag matching the interpreting check.
- Expected Immunefi impact: Fraud/quality thresholds silently misapplied, admitting rejectable captures
- Fast validation: Unit-test `run_update_all_configs` with a mismatched version tag asserting a hard error.
