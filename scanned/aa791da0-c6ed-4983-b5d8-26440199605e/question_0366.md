# Q0366: Replayed capture frames accepted by poll_extra (biometric_capture/mirror_sweep.rs)

## Question
Can an unprivileged attacker replay a previously captured frame sequence (screen playback, recorded IR video) into `poll_extra` in [src/plans/biometric_capture/mirror_sweep.rs](src/plans/biometric_capture/mirror_sweep.rs) with no per-session challenge/nonce binding, so a recording of another person passes as a live capture?

## Target
- File/function: [src/plans/biometric_capture/mirror_sweep.rs](src/plans/biometric_capture/mirror_sweep.rs) -> `poll_extra` (function)
- Entrypoint: Displaying recorded frames to the sensor during capture
- Attacker controls: the recorded sequence and its playback timing
- Exploit idea: Check `poll_extra` for any session-unique, unpredictable stimulus that a recording could not anticipate.
- Invariant to test: Every accepted capture is bound to an unpredictable per-session stimulus.
- Expected Immunefi impact: Signup completed using another person's recorded biometrics
- Fast validation: Integration test: replay a stored sequence into `poll_extra` and assert failure on the freshness check.
