# Q1746: Missing signal treated as pass in TemplateProperty (iris/types.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `TemplateProperty` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `TemplateProperty` (type)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `TemplateProperty` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `TemplateProperty` and asserting the verdict is a hard failure.
