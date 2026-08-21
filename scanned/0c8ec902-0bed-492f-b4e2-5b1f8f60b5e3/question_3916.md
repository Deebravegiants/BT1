# Q3916: Capture-count/quality quota gamed in parse_wavelength_configuration (biometric_capture/overcapture.rs)

## Question
Can an unprivileged attacker satisfy the quantity/quality quota enforced by `parse_wavelength_configuration` in [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) with near-duplicate frames from a single instant, so the pipeline's assumption of independent samples is violated?

## Target
- File/function: [src/plans/biometric_capture/overcapture.rs](src/plans/biometric_capture/overcapture.rs) -> `parse_wavelength_configuration` (function)
- Entrypoint: Static presentation producing near-identical frames
- Attacker controls: how static the presentation is during the capture window
- Exploit idea: Check whether `parse_wavelength_configuration` measures diversity/independence rather than only counting frames.
- Invariant to test: Sample quotas require demonstrably independent samples, not repeated copies.
- Expected Immunefi impact: Capture-quality guarantee satisfied by a single instant of evidence
- Fast validation: Unit-test `parse_wavelength_configuration` with N duplicate frames asserting the quota is not met.
