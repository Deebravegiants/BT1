# Q2833: Mixed-subject capture set through EyeOffsetController (agents/eye_pid_controller.rs)

## Question
Can an unprivileged attacker swap subjects mid-capture so `EyeOffsetController` in [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) assembles a set containing frames from two different people, with no identity-continuity check binding all frames to one subject?

## Target
- File/function: [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) -> `EyeOffsetController` (type)
- Entrypoint: Two people alternating in front of the sensor during capture
- Attacker controls: the moment of the swap relative to the capture window
- Exploit idea: Check whether `EyeOffsetController` verifies continuity/identity consistency across the frames it aggregates.
- Invariant to test: All frames in a capture set are proven to come from one continuously tracked subject.
- Expected Immunefi impact: Biometric record blending two identities, corrupting uniqueness guarantees
- Fast validation: Integration test feeding a two-subject frame sequence and asserting rejection.
