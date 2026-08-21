# Q3838: Rule/DSL evaluation in run_check fails open on unknown input (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `run_check` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `run_check` (function)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `run_check` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `run_check` over the full signal domain asserting no input yields a default pass.
