# Q2914: Bystander capture via subject selection in Ellipticity (iris/types.rs)

## Question
Can an unprivileged attacker stand behind or beside the enrolling user so `Ellipticity` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) selects or includes the bystander's face/iris in the processed output without their consent?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `Ellipticity` (type)
- Entrypoint: Positioning a second person in the camera field during capture
- Attacker controls: position and prominence of the additional subject
- Exploit idea: Check the selection rule in `Ellipticity` (largest, first, nearest) against a consent-bound identity rule.
- Invariant to test: Only the consenting, tracked subject's biometrics are processed and retained.
- Expected Immunefi impact: Non-consenting bystander's biometric data captured and processed
- Fast validation: Integration test with a two-subject scene asserting only the tracked subject is processed.
