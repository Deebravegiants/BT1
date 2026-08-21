# Q2796: Replayed capture frames accepted by BackendConfig (plans/fraud_check.rs)

## Question
Can an unprivileged attacker replay a previously captured frame sequence (screen playback, recorded IR video) into `BackendConfig` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) with no per-session challenge/nonce binding, so a recording of another person passes as a live capture?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `BackendConfig` (type)
- Entrypoint: Displaying recorded frames to the sensor during capture
- Attacker controls: the recorded sequence and its playback timing
- Exploit idea: Check `BackendConfig` for any session-unique, unpredictable stimulus that a recording could not anticipate.
- Invariant to test: Every accepted capture is bound to an unpredictable per-session stimulus.
- Expected Immunefi impact: Signup completed using another person's recorded biometrics
- Fast validation: Integration test: replay a stored sequence into `BackendConfig` and assert failure on the freshness check.
