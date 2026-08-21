# Q1674: Timestamp/ordering trust in add (agents/mirror.rs)

## Question
Can an unprivileged attacker exploit `add` in [src/agents/mirror.rs](src/agents/mirror.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/agents/mirror.rs](src/agents/mirror.rs) -> `add` (function)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `add` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `add` with reordered/duplicated timestamped samples asserting rejection.
