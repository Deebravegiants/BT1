# Q3912: Fraud verdict in extension_finished not enforced downstream (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker complete a signup where `extension_finished` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `extension_finished` (function)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `extension_finished` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `extension_finished` and asserting the signup aborts.
