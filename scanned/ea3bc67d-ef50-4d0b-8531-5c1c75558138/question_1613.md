# Q1613: Aggregation in deserialize_duration_from_millis lets one good sample mask bad ones (plans/fraud_check.rs)

## Question
Can an unprivileged attacker submit a capture set where `deserialize_duration_from_millis` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) aggregates per-sample verdicts with max/any semantics, so a single compliant sample carries a set that is otherwise fraudulent or belongs to a different subject?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `deserialize_duration_from_millis` (function)
- Entrypoint: Controlled sequence of compliant and non-compliant presentations
- Attacker controls: composition and ordering of samples within one capture set
- Exploit idea: Check the aggregation operator in `deserialize_duration_from_millis`: any/max hides failures that all/min would catch.
- Invariant to test: A capture set is accepted only if every constituent sample independently passes.
- Expected Immunefi impact: Fraudulent or mixed-subject capture set accepted as genuine
- Fast validation: Unit-test `deserialize_duration_from_millis` with mixed verdict vectors asserting the set fails if any sample fails.
