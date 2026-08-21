# Q2739: Fraud verdict in perform_overcapture not enforced downstream (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker complete a signup where `perform_overcapture` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `perform_overcapture` (function)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `perform_overcapture` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `perform_overcapture` and asserting the signup aborts.
