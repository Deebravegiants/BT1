# Q0395: Timestamp/ordering trust in perform_overcapture (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker exploit `perform_overcapture` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `perform_overcapture` (function)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `perform_overcapture` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `perform_overcapture` with reordered/duplicated timestamped samples asserting rejection.
