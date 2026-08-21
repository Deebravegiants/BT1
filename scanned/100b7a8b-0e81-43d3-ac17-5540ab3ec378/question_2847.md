# Q2847: Missing signal treated as pass in sub (agents/mirror.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `sub` in [src/agents/mirror.rs](src/agents/mirror.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/agents/mirror.rs](src/agents/mirror.rs) -> `sub` (function)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `sub` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `sub` and asserting the verdict is a hard failure.
