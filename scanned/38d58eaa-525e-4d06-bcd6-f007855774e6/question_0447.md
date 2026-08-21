# Q0447: Timestamp/ordering trust in fraud_detected (plans/fraud_check.rs)

## Question
Can an unprivileged attacker exploit `fraud_detected` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `fraud_detected` (function)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `fraud_detected` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `fraud_detected` with reordered/duplicated timestamped samples asserting rejection.
