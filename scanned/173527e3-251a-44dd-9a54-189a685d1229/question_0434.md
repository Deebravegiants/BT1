# Q0434: Bystander capture via subject selection in Error (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker stand behind or beside the enrolling user so `Error` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) selects or includes the bystander's face/iris in the processed output without their consent?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `Error` (type)
- Entrypoint: Positioning a second person in the camera field during capture
- Attacker controls: position and prominence of the additional subject
- Exploit idea: Check the selection rule in `Error` (largest, first, nearest) against a consent-bound identity rule.
- Invariant to test: Only the consenting, tracked subject's biometrics are processed and retained.
- Expected Immunefi impact: Non-consenting bystander's biometric data captured and processed
- Fast validation: Integration test with a two-subject scene asserting only the tracked subject is processed.
