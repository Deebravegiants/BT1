# Q3966: Fraud verdict in new not enforced downstream (plans/fraud_check.rs)

## Question
Can an unprivileged attacker complete a signup where `new` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `new` (function)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `new` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `new` and asserting the signup aborts.
