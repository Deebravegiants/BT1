# Q2714: Timestamp/ordering trust in extension_finished (biometric_capture/mirror_sweep.rs)

## Question
Can an unprivileged attacker exploit `extension_finished` in [src/plans/biometric_capture/mirror_sweep.rs](src/plans/biometric_capture/mirror_sweep.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/plans/biometric_capture/mirror_sweep.rs](src/plans/biometric_capture/mirror_sweep.rs) -> `extension_finished` (function)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `extension_finished` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `extension_finished` with reordered/duplicated timestamped samples asserting rejection.
