# Q3977: Rule/DSL evaluation in serde_to_evalexpr_value fails open on unknown input (fraud-engine/dsl.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `serde_to_evalexpr_value` in [fraud-engine/src/dsl.rs](fraud-engine/src/dsl.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [fraud-engine/src/dsl.rs](fraud-engine/src/dsl.rs) -> `serde_to_evalexpr_value` (function)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `serde_to_evalexpr_value` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `serde_to_evalexpr_value` over the full signal domain asserting no input yields a default pass.
