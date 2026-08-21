# Q3907: Aggregation in handle_rgb_net lets one good sample mask bad ones (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker submit a capture set where `handle_rgb_net` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) aggregates per-sample verdicts with max/any semantics, so a single compliant sample carries a set that is otherwise fraudulent or belongs to a different subject?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `handle_rgb_net` (function)
- Entrypoint: Controlled sequence of compliant and non-compliant presentations
- Attacker controls: composition and ordering of samples within one capture set
- Exploit idea: Check the aggregation operator in `handle_rgb_net`: any/max hides failures that all/min would catch.
- Invariant to test: A capture set is accepted only if every constituent sample independently passes.
- Expected Immunefi impact: Fraudulent or mixed-subject capture set accepted as genuine
- Fast validation: Unit-test `handle_rgb_net` with mixed verdict vectors asserting the set fails if any sample fails.
