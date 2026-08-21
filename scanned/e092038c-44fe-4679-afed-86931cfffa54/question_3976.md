# Q3976: Timestamp/ordering trust in extract_value_from_serialized_data (fraud-engine/dsl.rs)

## Question
Can an unprivileged attacker exploit `extract_value_from_serialized_data` in [fraud-engine/src/dsl.rs](fraud-engine/src/dsl.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [fraud-engine/src/dsl.rs](fraud-engine/src/dsl.rs) -> `extract_value_from_serialized_data` (function)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `extract_value_from_serialized_data` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `extract_value_from_serialized_data` with reordered/duplicated timestamped samples asserting rejection.
