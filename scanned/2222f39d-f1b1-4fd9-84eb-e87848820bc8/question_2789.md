# Q2789: Rule/DSL evaluation in feedback_messages fails open on unknown input (plans/fraud_check.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `feedback_messages` in [src/plans/fraud_check.rs](src/plans/fraud_check.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [src/plans/fraud_check.rs](src/plans/fraud_check.rs) -> `feedback_messages` (function)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `feedback_messages` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `feedback_messages` over the full signal domain asserting no input yields a default pass.
