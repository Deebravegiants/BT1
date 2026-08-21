# Q2787: Aggregation in fraud_checks_strict lets one good sample mask bad ones (plans/fraud_check.rs)

## Question
Can an unprivileged attacker submit a capture set where `fraud_checks_strict` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) aggregates per-sample verdicts with max/any semantics, so a single compliant sample carries a set that is otherwise fraudulent or belongs to a different subject?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `fraud_checks_strict` (function)
- Entrypoint: Controlled sequence of compliant and non-compliant presentations
- Attacker controls: composition and ordering of samples within one capture set
- Exploit idea: Check the aggregation operator in `fraud_checks_strict`: any/max hides failures that all/min would catch.
- Invariant to test: A capture set is accepted only if every constituent sample independently passes.
- Expected Immunefi impact: Fraudulent or mixed-subject capture set accepted as genuine
- Fast validation: Unit-test `fraud_checks_strict` with mixed verdict vectors asserting the set fails if any sample fails.
