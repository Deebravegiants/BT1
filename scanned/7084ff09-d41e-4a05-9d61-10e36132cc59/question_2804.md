# Q2804: Replayed capture frames accepted by extract_value_from_serialized_data (fraud-engine/dsl.rs)

## Question
Can an unprivileged attacker replay a previously captured frame sequence (screen playback, recorded IR video) into `extract_value_from_serialized_data` in [fraud-engine/src/dsl.rs](fraud-engine/src/dsl.rs) with no per-session challenge/nonce binding, so a recording of another person passes as a live capture?

## Target
- File/function: [fraud-engine/src/dsl.rs](fraud-engine/src/dsl.rs) -> `extract_value_from_serialized_data` (function)
- Entrypoint: Displaying recorded frames to the sensor during capture
- Attacker controls: the recorded sequence and its playback timing
- Exploit idea: Check `extract_value_from_serialized_data` for any session-unique, unpredictable stimulus that a recording could not anticipate.
- Invariant to test: Every accepted capture is bound to an unpredictable per-session stimulus.
- Expected Immunefi impact: Signup completed using another person's recorded biometrics
- Fast validation: Integration test: replay a stored sequence into `extract_value_from_serialized_data` and assert failure on the freshness check.
