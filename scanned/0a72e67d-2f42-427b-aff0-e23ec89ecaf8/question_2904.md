# Q2904: Fraud verdict in EstimateOutput not enforced downstream (iris/mod.rs)

## Question
Can an unprivileged attacker complete a signup where `EstimateOutput` in [src/agents/python/iris/mod.rs](src/agents/python/iris/mod.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/agents/python/iris/mod.rs](src/agents/python/iris/mod.rs) -> `EstimateOutput` (type)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `EstimateOutput` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `EstimateOutput` and asserting the signup aborts.
