# Q0375: Rule/DSL evaluation in parse_configuration_value fails open on unknown input (biometric_capture/mirror_sweep.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `parse_configuration_value` in [src/plans/biometric_capture/mirror_sweep.rs](src/plans/biometric_capture/mirror_sweep.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [src/plans/biometric_capture/mirror_sweep.rs](src/plans/biometric_capture/mirror_sweep.rs) -> `parse_configuration_value` (function)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `parse_configuration_value` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `parse_configuration_value` over the full signal domain asserting no input yields a default pass.
