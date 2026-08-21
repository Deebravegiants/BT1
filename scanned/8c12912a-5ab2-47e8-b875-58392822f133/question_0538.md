# Q0538: Fraud verdict in LiquidLensController not enforced downstream (agents/ir_auto_focus.rs)

## Question
Can an unprivileged attacker complete a signup where `LiquidLensController` in [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) computes a failing fraud/quality verdict that is recorded for telemetry but never gates the enrollment or upload decision?

## Target
- File/function: [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) -> `LiquidLensController` (type)
- Entrypoint: Presenting a scene that trips the check
- Attacker controls: scene conditions that reliably produce the failing verdict
- Exploit idea: Trace the verdict produced by `LiquidLensController` to every consumer and check for an enforcement point.
- Invariant to test: Every negative verdict has a mandatory enforcement point before enrollment/upload.
- Expected Immunefi impact: Fraudulent signup completed despite a failing anti-fraud verdict
- Fast validation: Integration test forcing a failing verdict from `LiquidLensController` and asserting the signup aborts.
