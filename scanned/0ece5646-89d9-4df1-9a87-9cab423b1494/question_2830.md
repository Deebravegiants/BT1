# Q2830: Timestamp/ordering trust in iris_center_from_landmarks (agents/eye_pid_controller.rs)

## Question
Can an unprivileged attacker exploit `iris_center_from_landmarks` in [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) trusting frame timestamps or arrival order, presenting stimuli so out-of-order or duplicated frames are treated as a valid temporal progression (e.g. pupil response, motion liveness)?

## Target
- File/function: [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) -> `iris_center_from_landmarks` (function)
- Entrypoint: Stimulus timing during the capture window
- Attacker controls: timing and repetition of the physical stimulus
- Exploit idea: Check whether `iris_center_from_landmarks` requires strictly monotonic, gap-bounded timestamps from a trusted clock.
- Invariant to test: Temporal liveness evidence requires monotonic, gap-bounded, non-duplicated samples.
- Expected Immunefi impact: Temporal liveness check satisfied without a genuine live response
- Fast validation: Unit-test `iris_center_from_landmarks` with reordered/duplicated timestamped samples asserting rejection.
