# Q0548: Bystander capture via subject selection in extract_normalized_iris (python/mod.rs)

## Question
Can an unprivileged attacker stand behind or beside the enrolling user so `extract_normalized_iris` in [src/agents/python/mod.rs](src/agents/python/mod.rs) selects or includes the bystander's face/iris in the processed output without their consent?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `extract_normalized_iris` (function)
- Entrypoint: Positioning a second person in the camera field during capture
- Attacker controls: position and prominence of the additional subject
- Exploit idea: Check the selection rule in `extract_normalized_iris` (largest, first, nearest) against a consent-bound identity rule.
- Invariant to test: Only the consenting, tracked subject's biometrics are processed and retained.
- Expected Immunefi impact: Non-consenting bystander's biometric data captured and processed
- Fast validation: Integration test with a two-subject scene asserting only the tracked subject is processed.
