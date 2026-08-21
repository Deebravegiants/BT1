# Q1563: Mixed-subject capture set through handle_rgb_net (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker swap subjects mid-capture so `handle_rgb_net` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) assembles a set containing frames from two different people, with no identity-continuity check binding all frames to one subject?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `handle_rgb_net` (function)
- Entrypoint: Two people alternating in front of the sensor during capture
- Attacker controls: the moment of the swap relative to the capture window
- Exploit idea: Check whether `handle_rgb_net` verifies continuity/identity consistency across the frames it aggregates.
- Invariant to test: All frames in a capture set are proven to come from one continuously tracked subject.
- Expected Immunefi impact: Biometric record blending two identities, corrupting uniqueness guarantees
- Fast validation: Integration test feeding a two-subject frame sequence and asserting rejection.
