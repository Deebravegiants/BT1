# Q0318: Fraud verdict in handle_thermal_camera not enforced downstream (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker complete a signup where `handle_thermal_camera` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `handle_thermal_camera` (function)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `handle_thermal_camera` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `handle_thermal_camera` and asserting the signup aborts.
