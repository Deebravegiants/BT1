# Q1800: Missing signal treated as pass in EstimateOutput (python/ir_net.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `EstimateOutput` in [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/agents/python/ir_net.rs](src/agents/python/ir_net.rs) -> `EstimateOutput` (type)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `EstimateOutput` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `EstimateOutput` and asserting the verdict is a hard failure.
