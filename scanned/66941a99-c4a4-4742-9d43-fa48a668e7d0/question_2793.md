# Q2793: Mixed-subject capture set through as_datadog_tags_with_config (plans/fraud_check.rs)

## Question
Can an unprivileged attacker swap subjects mid-capture so `as_datadog_tags_with_config` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) assembles a set containing frames from two different people, with no identity-continuity check binding all frames to one subject?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `as_datadog_tags_with_config` (function)
- Entrypoint: Two people alternating in front of the sensor during capture
- Attacker controls: the moment of the swap relative to the capture window
- Exploit idea: Check whether `as_datadog_tags_with_config` verifies continuity/identity consistency across the frames it aggregates.
- Invariant to test: All frames in a capture set are proven to come from one continuously tracked subject.
- Expected Immunefi impact: Biometric record blending two identities, corrupting uniqueness guarantees
- Fast validation: Integration test feeding a two-subject frame sequence and asserting rejection.
