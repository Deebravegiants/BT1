# Q2818: Rule/DSL evaluation in default fails open on unknown input (agents/eye_tracker.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `default` in [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [src/agents/eye_tracker.rs](src/agents/eye_tracker.rs) -> `default` (function)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `default` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `default` over the full signal domain asserting no input yields a default pass.
