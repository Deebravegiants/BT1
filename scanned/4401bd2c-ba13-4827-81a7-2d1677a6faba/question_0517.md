# Q0517: Replayed capture frames accepted by Output (agents/thermal.rs)

## Question
Can an unprivileged attacker replay a previously captured frame sequence (screen playback, recorded IR video) into `Output` in [src/agents/thermal.rs](src/agents/thermal.rs) with no per-session challenge/nonce binding, so a recording of another person passes as a live capture?

## Target
- File/function: [src/agents/thermal.rs](src/agents/thermal.rs) -> `Output` (type)
- Entrypoint: Displaying recorded frames to the sensor during capture
- Attacker controls: the recorded sequence and its playback timing
- Exploit idea: Check `Output` for any session-unique, unpredictable stimulus that a recording could not anticipate.
- Invariant to test: Every accepted capture is bound to an unpredictable per-session stimulus.
- Expected Immunefi impact: Signup completed using another person's recorded biometrics
- Fast validation: Integration test: replay a stored sequence into `Output` and assert failure on the freshness check.
