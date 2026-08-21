# Q1595: Mixed-subject capture set through run_mega_agent_one (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker swap subjects mid-capture so `run_mega_agent_one` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) assembles a set containing frames from two different people, with no identity-continuity check binding all frames to one subject?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `run_mega_agent_one` (function)
- Entrypoint: Two people alternating in front of the sensor during capture
- Attacker controls: the moment of the swap relative to the capture window
- Exploit idea: Check whether `run_mega_agent_one` verifies continuity/identity consistency across the frames it aggregates.
- Invariant to test: All frames in a capture set are proven to come from one continuously tracked subject.
- Expected Immunefi impact: Biometric record blending two identities, corrupting uniqueness guarantees
- Fast validation: Integration test feeding a two-subject frame sequence and asserting rejection.
