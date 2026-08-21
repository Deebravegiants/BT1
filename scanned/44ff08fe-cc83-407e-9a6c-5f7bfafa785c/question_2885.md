# Q2885: Fraud verdict in check_model_version not enforced downstream (python/mod.rs)

## Question
Can an unprivileged attacker complete a signup where `check_model_version` in [src/agents/python/mod.rs](src/agents/python/mod.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `check_model_version` (function)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `check_model_version` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `check_model_version` and asserting the signup aborts.
