# Q0456: Selection of the 'best' sample in lib is attacker-steerable (fraud-engine/lib.rs)

## Question
Can an unprivileged attacker bias the selection criterion in `lib` in [fraud-engine/src/lib.rs](fraud-engine/src/lib.rs) so the frame chosen for enrollment is the one that most favours a spoof (highest score under a metric the artifact optimizes) rather than the most genuine one?

## Target
- File/function: [fraud-engine/src/lib.rs](fraud-engine/src/lib.rs) -> `lib` (module)
- Entrypoint: Presenting a scene optimized for the selection metric
- Attacker controls: the property the selection metric ranks on
- Exploit idea: Check whether the selection metric in `lib` is independent of the properties an artifact can maximize.
- Invariant to test: Selection ranks on genuineness-correlated metrics that artifacts cannot maximize.
- Expected Immunefi impact: Spoof-favourable sample chosen for enrollment
- Fast validation: Differential test ranking genuine vs. artifact-derived samples through `lib`.
