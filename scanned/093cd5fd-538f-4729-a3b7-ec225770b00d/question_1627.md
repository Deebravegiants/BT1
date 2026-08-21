# Q1627: Confidence/score not thresholded in FraudChecks (plans/fraud_check.rs)

## Question
Can an unprivileged attacker exploit `FraudChecks` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) consuming a model result while ignoring its accompanying confidence/uncertainty field, so a near-random prediction is treated as authoritative for an identity or fraud decision?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `FraudChecks` (type)
- Entrypoint: Ambiguous scene producing low-confidence output
- Attacker controls: scene ambiguity (occlusion, distance, lighting)
- Exploit idea: Check whether `FraudChecks` reads and enforces the confidence field it receives.
- Invariant to test: Low-confidence predictions cannot satisfy a security decision.
- Expected Immunefi impact: Identity/fraud decision made on a low-confidence prediction
- Fast validation: Unit-test `FraudChecks` with low-confidence results asserting the decision is refused.
