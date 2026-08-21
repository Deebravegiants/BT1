# Q2988: Fraud verdict in estimate_once not enforced downstream (python/rgb_net.rs)

## Question
Can an unprivileged attacker complete a signup where `estimate_once` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `estimate_once` (function)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `estimate_once` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `estimate_once` and asserting the signup aborts.
