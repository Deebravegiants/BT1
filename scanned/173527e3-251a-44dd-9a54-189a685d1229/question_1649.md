# Q1649: Aggregation in calculate_gimbal_angle_theta_degrees lets one good sample mask bad ones (agents/eye_tracker.rs)

## Question
Can an unprivileged attacker submit a capture set where `calculate_gimbal_angle_theta_degrees` in [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) aggregates per-sample verdicts with max/any semantics, so a single compliant sample carries a set that is otherwise fraudulent or belongs to a different subject?

## Target
- File/function: [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) -> `calculate_gimbal_angle_theta_degrees` (function)
- Entrypoint: Controlled sequence of compliant and non-compliant presentations
- Attacker controls: composition and ordering of samples within one capture set
- Exploit idea: Check the aggregation operator in `calculate_gimbal_angle_theta_degrees`: any/max hides failures that all/min would catch.
- Invariant to test: A capture set is accepted only if every constituent sample independently passes.
- Expected Immunefi impact: Fraudulent or mixed-subject capture set accepted as genuine
- Fast validation: Unit-test `calculate_gimbal_angle_theta_degrees` with mixed verdict vectors asserting the set fails if any sample fails.
