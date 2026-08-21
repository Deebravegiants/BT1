# Q0503: Capture-count/quality quota gamed in sub (agents/mirror.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `sub` in [src/agents/mirror.rs](src/agents/mirror.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/agents/mirror.rs](src/agents/mirror.rs) -> `sub` (function)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `sub` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `sub` with N duplicate frames asserting the quota is not met.
