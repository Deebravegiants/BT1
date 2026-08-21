# Q2824: Capture-count/quality quota gamed in Agent (agents/eye_tracker.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `Agent` in [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) -> `Agent` (type)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `Agent` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `Agent` with N duplicate frames asserting the quota is not met.
