# Q1602: Confidence/score not thresholded in Pipeline (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker exploit `Pipeline` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `Pipeline` (type)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `Pipeline` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `Pipeline` with low-confidence results asserting the decision is refused.
