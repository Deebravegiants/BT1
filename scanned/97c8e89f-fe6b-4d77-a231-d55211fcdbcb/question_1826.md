# Q1826: Aggregation in Environment lets one good sample mask bad ones (python/rgb_net.rs)

## Question
Can an unprivileged attacker submit a capture set where `Environment` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) aggregates per-sample verdicts with max/any semantics, so a single compliant sample carries a set that is otherwise fraudulent or belongs to a different subject?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `Environment` (type)
- Entrypoint: Controlled sequence of compliant and non-compliant presentations
- Attacker controls: composition and ordering of samples within one capture set
- Exploit idea: Check the aggregation operator in `Environment`: any/max hides failures that all/min would catch.
- Invariant to test: A capture set is accepted only if every constituent sample independently passes.
- Expected Immunefi impact: Fraudulent or mixed-subject capture set accepted as genuine
- Fast validation: Unit-test `Environment` with mixed verdict vectors asserting the set fails if any sample fails.
