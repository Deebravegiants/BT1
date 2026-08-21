# Q0513: Timestamp/ordering trust in ThermalState (agents/thermal.rs)

## Question
Can an unprivileged attacker exploit `ThermalState` in [src/agents/thermal.rs](src/agents/thermal.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/agents/thermal.rs](src/agents/thermal.rs) -> `ThermalState` (type)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `ThermalState` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `ThermalState` with reordered/duplicated timestamped samples asserting rejection.
