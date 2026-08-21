# Q3972: Rule/DSL evaluation in lib fails open on unknown input (fraud-engine/lib.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `lib` in [fraud-engine/src/lib.rs](fraud-engine/src/lib.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [fraud-engine/src/lib.rs](fraud-engine/src/lib.rs) -> `lib` (module)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `lib` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `lib` over the full signal domain asserting no input yields a default pass.
