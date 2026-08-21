# Q1678: Fraud verdict in Command not enforced downstream (agents/mirror.rs)

## Question
Can an unprivileged attacker complete a signup where `Command` in [src/agents/mirror.rs](src/agents/mirror.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/agents/mirror.rs](src/agents/mirror.rs) -> `Command` (type)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `Command` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `Command` and asserting the signup aborts.
