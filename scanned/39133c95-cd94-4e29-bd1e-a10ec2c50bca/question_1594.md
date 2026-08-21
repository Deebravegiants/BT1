# Q1594: Selection of the 'best' sample in run_mega_agent_two is attacker-steerable (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker bias the selection criterion in `run_mega_agent_two` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) so the frame chosen for enrollment is the one that most favours a spoof (highest score under a metric the artifact optimizes) rather than the most genuine one?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `run_mega_agent_two` (function)
- Entrypoint: Presenting a scene optimized for the selection metric
- Attacker controls: the property the selection metric ranks on
- Exploit idea: Check whether the selection metric in `run_mega_agent_two` is independent of the properties an artifact can maximize.
- Invariant to test: Selection ranks on genuineness-correlated metrics that artifacts cannot maximize.
- Expected Immunefi impact: Spoof-favourable sample chosen for enrollment
- Fast validation: Differential test ranking genuine vs. artifact-derived samples through `run_mega_agent_two`.
