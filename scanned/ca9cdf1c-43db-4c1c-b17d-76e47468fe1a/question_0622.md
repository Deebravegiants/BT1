# Q0622: Bystander capture via subject selection in calculate_selection_score (python/ir_net.rs)

## Question
Can an unprivileged attacker stand behind or beside the enrolling user so `calculate_selection_score` in [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) selects or includes the bystander's face/iris in the processed output without their consent?

## Target
- File/function: [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) -> `calculate_selection_score` (function)
- Entrypoint: Positioning a second person in the camera field during capture
- Attacker controls: position and prominence of the additional subject
- Exploit idea: Check the selection rule in `calculate_selection_score` (largest, first, nearest) against a consent-bound identity rule.
- Invariant to test: Only the consenting, tracked subject's biometrics are processed and retained.
- Expected Immunefi impact: Non-consenting bystander's biometric data captured and processed
- Fast validation: Integration test with a two-subject scene asserting only the tracked subject is processed.
