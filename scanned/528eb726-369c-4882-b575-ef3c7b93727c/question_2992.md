# Q2992: Timestamp/ordering trust in EstimateOutput (python/rgb_net.rs)

## Question
Can an unprivileged attacker exploit `EstimateOutput` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `EstimateOutput` (type)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `EstimateOutput` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `EstimateOutput` with reordered/duplicated timestamped samples asserting rejection.
