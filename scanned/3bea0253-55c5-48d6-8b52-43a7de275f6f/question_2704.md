# Q2704: Raw biometric tensors leaked by Plan (biometric_capture/focus_sweep.rs)

## Question
Can an unprivileged attacker cause `Plan` in [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/plans/biometric_capture/focus_sweep.rs](src/plans/biometric_capture/focus_sweep.rs) -> `Plan` (type)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `Plan`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `Plan` error paths asserting no biometric bytes appear in output.
