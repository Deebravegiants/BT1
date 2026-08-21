# Q2846: Aggregation in add lets one good sample mask bad ones (agents/mirror.rs)

## Question
Can an unprivileged attacker submit a capture set where `add` in [src/agents/mirror.rs](src/agents/mirror.rs) aggregates per-sample verdicts with max/any semantics, so a single compliant sample carries a set that is otherwise fraudulent or belongs to a different subject?

## Target
- File/function: [src/agents/mirror.rs](src/agents/mirror.rs) -> `add` (function)
- Entrypoint: Controlled sequence of compliant and non-compliant presentations
- Attacker controls: composition and ordering of samples within one capture set
- Exploit idea: Check the aggregation operator in `add`: any/max hides failures that all/min would catch.
- Invariant to test: A capture set is accepted only if every constituent sample independently passes.
- Expected Immunefi impact: Fraudulent or mixed-subject capture set accepted as genuine
- Fast validation: Unit-test `add` with mixed verdict vectors asserting the set fails if any sample fails.
