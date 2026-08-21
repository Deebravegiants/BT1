# Q1609: Timestamp/ordering trust in to_packed_base64 (biometric_pipeline/code.rs)

## Question
Can an unprivileged attacker exploit `to_packed_base64` in [src/plans/biometric_pipeline/code.rs](src/plans/biometric_pipeline/code.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/plans/biometric_pipeline/code.rs](src/plans/biometric_pipeline/code.rs) -> `to_packed_base64` (function)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `to_packed_base64` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `to_packed_base64` with reordered/duplicated timestamped samples asserting rejection.
