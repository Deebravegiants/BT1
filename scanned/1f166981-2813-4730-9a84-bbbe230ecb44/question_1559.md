# Q1559: Rule/DSL evaluation in perform_multi_wavelength fails open on unknown input (biometric_capture/multi_wavelength.rs)

## Question
Can an unprivileged attacker produce an input combination that makes the rule evaluation in `perform_multi_wavelength` in [src/plans/biometric_capture/multi_wavelength.rs](src/plans/biometric_capture/multi_wavelength.rs) hit an unknown/unhandled case that resolves to 'no fraud detected' rather than to an error?

## Target
- File/function: [src/plans/biometric_capture/multi_wavelength.rs](src/plans/biometric_capture/multi_wavelength.rs) -> `perform_multi_wavelength` (function)
- Entrypoint: Scene conditions producing an unusual signal combination
- Attacker controls: the combination of measured signals fed to the rule engine
- Exploit idea: Enumerate the match arms/branches in `perform_multi_wavelength` and identify the catch-all's polarity.
- Invariant to test: Unhandled signal combinations resolve to a hard failure, never to a clean verdict.
- Expected Immunefi impact: Anti-fraud engine returning a pass for an unclassifiable capture
- Fast validation: Property-test `perform_multi_wavelength` over the full signal domain asserting no input yields a default pass.
