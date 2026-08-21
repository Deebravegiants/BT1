# Q3961: Selection of the 'best' sample in feedback_messages is attacker-steerable (plans/fraud_check.rs)

## Question
Can an unprivileged attacker bias the selection criterion in `feedback_messages` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) so the frame chosen for enrollment is the one that most favours a spoof (highest score under a metric the artifact optimizes) rather than the most genuine one?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `feedback_messages` (function)
- Entrypoint: Presenting a scene optimized for the selection metric
- Attacker controls: the property the selection metric ranks on
- Exploit idea: Check whether the selection metric in `feedback_messages` is independent of the properties an artifact can maximize.
- Invariant to test: Selection ranks on genuineness-correlated metrics that artifacts cannot maximize.
- Expected Immunefi impact: Spoof-favourable sample chosen for enrollment
- Fast validation: Differential test ranking genuine vs. artifact-derived samples through `feedback_messages`.
