# Q0530: Timestamp/ordering trust in set_min_sharpness (agents/ir_auto_focus.rs)

## Question
Can an unprivileged attacker exploit `set_min_sharpness` in [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) -> `set_min_sharpness` (function)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `set_min_sharpness` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `set_min_sharpness` with reordered/duplicated timestamped samples asserting rejection.
