# Q3981: Capture-count/quality quota gamed in Pipeline (fraud-engine/pipeline.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `Pipeline` in [fraud-engine/src/pipeline.rs](fraud-engine/src/pipeline.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [fraud-engine/src/pipeline.rs](fraud-engine/src/pipeline.rs) -> `Pipeline` (type)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `Pipeline` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `Pipeline` with N duplicate frames asserting the quota is not met.
