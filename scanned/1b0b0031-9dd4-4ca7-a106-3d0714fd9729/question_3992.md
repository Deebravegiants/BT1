# Q3992: Rule/DSL evaluation in calculate_gimbal_angle_phi_degrees fails open on unknown input (agents/eye_tracker.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `calculate_gimbal_angle_phi_degrees` in [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) -> `calculate_gimbal_angle_phi_degrees` (function)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `calculate_gimbal_angle_phi_degrees` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `calculate_gimbal_angle_phi_degrees` over the full signal domain asserting no input yields a default pass.
