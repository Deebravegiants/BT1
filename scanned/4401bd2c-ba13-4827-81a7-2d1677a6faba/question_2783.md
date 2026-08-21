# Q2783: Rule/DSL evaluation in pack_bits fails open on unknown input (biometric_pipeline/code.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `pack_bits` in [src/plans/biometric_pipeline/code.rs](src/plans/biometric_pipeline/code.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [src/plans/biometric_pipeline/code.rs](src/plans/biometric_pipeline/code.rs) -> `pack_bits` (function)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `pack_bits` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `pack_bits` over the full signal domain asserting no input yields a default pass.
