# Q3984: Timestamp/ordering trust in to_datadog_tags (fraud-engine/report.rs)

## Question
Can an unprivileged attacker exploit `to_datadog_tags` in [fraud-engine/src/report.rs](fraud-engine/src/report.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [fraud-engine/src/report.rs](fraud-engine/src/report.rs) -> `to_datadog_tags` (function)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `to_datadog_tags` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `to_datadog_tags` with reordered/duplicated timestamped samples asserting rejection.
