# Q0482: Timestamp/ordering trust in run (agents/eye_pid_controller.rs)

## Question
Can an unprivileged attacker exploit `run` in [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) -> `run` (function)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `run` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `run` with reordered/duplicated timestamped samples asserting rejection.
