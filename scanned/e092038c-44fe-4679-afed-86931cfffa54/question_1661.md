# Q1661: Capture-count/quality quota gamed in EyeOffsetController (agents/eye_pid_controller.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `EyeOffsetController` in [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/agents/eye_pid_controller.rs](src/agents/eye_pid_controller.rs) -> `EyeOffsetController` (type)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `EyeOffsetController` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `EyeOffsetController` with N duplicate frames asserting the quota is not met.
