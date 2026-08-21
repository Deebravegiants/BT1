# Q0496: Capture-count/quality quota gamed in Log (agents/distance.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `Log` in [src/agents/distance.rs](src/agents/distance.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/agents/distance.rs](src/agents/distance.rs) -> `Log` (type)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `Log` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `Log` with N duplicate frames asserting the quota is not met.
