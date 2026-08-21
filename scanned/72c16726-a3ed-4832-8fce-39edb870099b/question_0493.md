# Q0493: Selection of the 'best' sample in Status is attacker-steerable (agents/distance.rs)

## Question
Can an unprivileged attacker bias the selection criterion in `Status` in [src/agents/distance.rs](src/agents/distance.rs) so the frame chosen for enrollment is the one that most favours a spoof (highest score under a metric the artifact optimizes) rather than the most genuine one?

## Target
- File/function: [src/agents/distance.rs](src/agents/distance.rs) -> `Status` (type)
- Entrypoint: Presenting a scene optimized for the selection metric
- Attacker controls: the property the selection metric ranks on
- Exploit idea: Check whether the selection metric in `Status` is independent of the properties an artifact can maximize.
- Invariant to test: Selection ranks on genuineness-correlated metrics that artifacts cannot maximize.
- Expected Immunefi impact: Spoof-favourable sample chosen for enrollment
- Fast validation: Differential test ranking genuine vs. artifact-derived samples through `Status`.
