# Q1733: Rule/DSL evaluation in Environment fails open on unknown input (iris/mod.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `Environment` in [src/agents/python/iris/mod.rs](src/agents/python/iris/mod.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [src/agents/python/iris/mod.rs](src/agents/python/iris/mod.rs) -> `Environment` (type)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `Environment` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `Environment` over the full signal domain asserting no input yields a default pass.
