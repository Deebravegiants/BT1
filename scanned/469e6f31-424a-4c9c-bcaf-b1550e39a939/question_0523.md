# Q0523: Replayed capture frames accepted by Agent (agents/ir_auto_exposure.rs)

## Question
Can an unprivileged attacker replay a previously captured frame sequence (screen playback, recorded IR video) into `Agent` in [src/agents/ir_auto_exposure.rs](src/agents/ir_auto_exposure.rs) with no per-session challenge/nonce binding, so a recording of another person passes as a live capture?

## Target
- File/function: [src/agents/ir_auto_exposure.rs](src/agents/ir_auto_exposure.rs) -> `Agent` (type)
- Entrypoint: Displaying recorded frames to the sensor during capture
- Attacker controls: the recorded sequence and its playback timing
- Exploit idea: Check `Agent` for any session-unique, unpredictable stimulus that a recording could not anticipate.
- Invariant to test: Every accepted capture is bound to an unpredictable per-session stimulus.
- Expected Immunefi impact: Signup completed using another person's recorded biometrics
- Fast validation: Integration test: replay a stored sequence into `Agent` and assert failure on the freshness check.
