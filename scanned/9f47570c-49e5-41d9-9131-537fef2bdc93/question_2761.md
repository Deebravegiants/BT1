# Q2761: Fraud verdict in handle_ir_net not enforced downstream (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker complete a signup where `handle_ir_net` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `handle_ir_net` (function)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `handle_ir_net` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `handle_ir_net` and asserting the signup aborts.
