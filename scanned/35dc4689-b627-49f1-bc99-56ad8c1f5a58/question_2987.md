# Q2987: Rule/DSL evaluation in extract_point fails open on unknown input (python/rgb_net.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `extract_point` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `extract_point` (function)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `extract_point` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `extract_point` over the full signal domain asserting no input yields a default pass.
