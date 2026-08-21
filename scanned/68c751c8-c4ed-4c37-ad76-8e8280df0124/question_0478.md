# Q0478: Fraud verdict in calculate_mirror_angles not enforced downstream (agents/eye_tracker.rs)

## Question
Can an unprivileged attacker complete a signup where `calculate_mirror_angles` in [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) -> `calculate_mirror_angles` (function)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `calculate_mirror_angles` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `calculate_mirror_angles` and asserting the signup aborts.
