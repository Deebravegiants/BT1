# Q1708: Rule/DSL evaluation in Agent fails open on unknown input (agents/ir_auto_focus.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `Agent` in [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [src/agents/ir_auto_focus.rs](src/agents/ir_auto_focus.rs) -> `Agent` (type)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `Agent` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `Agent` over the full signal domain asserting no input yields a default pass.
