# Q1682: Fraud verdict in get_highest_thermal_state not enforced downstream (agents/thermal.rs)

## Question
Can an unprivileged attacker complete a signup where `get_highest_thermal_state` in [src/agents/thermal.rs](src/agents/thermal.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/agents/thermal.rs](src/agents/thermal.rs) -> `get_highest_thermal_state` (function)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `get_highest_thermal_state` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `get_highest_thermal_state` and asserting the signup aborts.
