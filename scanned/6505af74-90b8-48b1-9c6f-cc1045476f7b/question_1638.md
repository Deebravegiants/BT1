# Q1638: Missing signal treated as pass in Check (fraud-engine/pipeline.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `Check` in [fraud-engine/src/pipeline.rs](fraud-engine/src/pipeline.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [fraud-engine/src/pipeline.rs](fraud-engine/src/pipeline.rs) -> `Check` (type)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `Check` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `Check` and asserting the verdict is a hard failure.
