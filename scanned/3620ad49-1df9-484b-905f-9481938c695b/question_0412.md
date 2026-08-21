# Q0412: Timestamp/ordering trust in Plan (biometric_capture/pupil_contraction.rs)

## Question
Can an unprivileged attacker exploit `Plan` in [src/plans/biometric_capture/pupil_contraction.rs](src/plans/biometric_capture/pupil_contraction.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/plans/biometric_capture/pupil_contraction.rs](src/plans/biometric_capture/pupil_contraction.rs) -> `Plan` (type)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `Plan` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `Plan` with reordered/duplicated timestamped samples asserting rejection.
