# Q1498: Confidence/score not thresholded in is_last_objective (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker exploit `is_last_objective` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `is_last_objective` (function)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `is_last_objective` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `is_last_objective` with low-confidence results asserting the decision is refused.
