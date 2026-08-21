# Q2879: Aggregation in compute_theoretical_focus_setting lets one good sample mask bad ones (agents/ir_auto_focus.rs)

## Question
Can an unprivileged attacker submit a capture set where `compute_theoretical_focus_setting` in [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) aggregates per-sample verdicts with max/any semantics, so a single compliant sample carries a set that is otherwise fraudulent or belongs to a different subject?

## Target
- File/function: [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) -> `compute_theoretical_focus_setting` (function)
- Entrypoint: Controlled sequence of compliant and non-compliant presentations
- Attacker controls: composition and ordering of samples within one capture set
- Exploit idea: Check the aggregation operator in `compute_theoretical_focus_setting`: any/max hides failures that all/min would catch.
- Invariant to test: A capture set is accepted only if every constituent sample independently passes.
- Expected Immunefi impact: Fraudulent or mixed-subject capture set accepted as genuine
- Fast validation: Unit-test `compute_theoretical_focus_setting` with mixed verdict vectors asserting the set fails if any sample fails.
