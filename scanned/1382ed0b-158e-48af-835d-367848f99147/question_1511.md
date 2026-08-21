# Q1511: Fraud verdict in Output not enforced downstream (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker complete a signup where `Output` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `Output` (type)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `Output` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `Output` and asserting the signup aborts.
