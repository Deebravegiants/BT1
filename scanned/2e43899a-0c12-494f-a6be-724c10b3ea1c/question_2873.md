# Q2873: Missing signal treated as pass in new (agents/ir_auto_focus.rs)

## Question
Can an unprivileged attacker make a required signal unavailable to `new` in [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) (agent not ready, sensor stalled, inference error) so its absence is coerced to a default that counts as a passing check?

## Target
- File/function: [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) -> `new` (function)
- Entrypoint: Scene or timing conditions that starve the signal
- Attacker controls: which sensor/agent is starved and for how long
- Exploit idea: Check whether `new` distinguishes 'checked and passed' from 'not checked'.
- Invariant to test: Absent evidence is never equivalent to passing evidence.
- Expected Immunefi impact: Signup accepted with a mandatory anti-fraud check never executed
- Fast validation: Fault-injection test removing each input to `new` and asserting the verdict is a hard failure.
