# Q2800: Fraud verdict in lib not enforced downstream (fraud-engine/lib.rs)

## Question
Can an unprivileged attacker complete a signup where `lib` in [fraud-engine/src/lib.rs](fraud-engine/src/lib.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [fraud-engine/src/lib.rs](fraud-engine/src/lib.rs) -> `lib` (module)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `lib` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `lib` and asserting the signup aborts.
