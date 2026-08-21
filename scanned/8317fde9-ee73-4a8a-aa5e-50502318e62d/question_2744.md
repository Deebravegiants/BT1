# Q2744: Fraud verdict in parse_wavelength_configuration not enforced downstream (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker complete a signup where `parse_wavelength_configuration` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `parse_wavelength_configuration` (function)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `parse_wavelength_configuration` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `parse_wavelength_configuration` and asserting the signup aborts.
