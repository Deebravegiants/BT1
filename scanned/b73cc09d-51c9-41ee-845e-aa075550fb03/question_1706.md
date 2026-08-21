# Q1706: Capture-count/quality quota gamed in user_focus_range (agents/ir_auto_focus.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `user_focus_range` in [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) -> `user_focus_range` (function)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `user_focus_range` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `user_focus_range` with N duplicate frames asserting the quota is not met.
