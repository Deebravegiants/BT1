# Q0526: Timestamp/ordering trust in ExposureController (agents/ir_auto_exposure.rs)

## Question
Can an unprivileged attacker exploit `ExposureController` in [src/agents/ir_auto_exposure.rs](src/agents/ir_auto_exposure.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/agents/ir_auto_exposure.rs](src/agents/ir_auto_exposure.rs) -> `ExposureController` (type)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `ExposureController` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `ExposureController` with reordered/duplicated timestamped samples asserting rejection.
