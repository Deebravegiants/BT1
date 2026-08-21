# Q3965: Capture-count/quality quota gamed in as_datadog_tags_with_config (plans/fraud_check.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `as_datadog_tags_with_config` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `as_datadog_tags_with_config` (function)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `as_datadog_tags_with_config` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `as_datadog_tags_with_config` with N duplicate frames asserting the quota is not met.
