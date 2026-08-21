# Q2989: Missing signal treated as pass in Model (python/rgb_net.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `Model` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `Model` (type)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `Model` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `Model` and asserting the verdict is a hard failure.
