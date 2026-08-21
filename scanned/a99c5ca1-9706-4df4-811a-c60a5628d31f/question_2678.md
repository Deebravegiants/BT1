# Q2678: Raw biometric tensors leaked by SelfCustodyCandidate (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker cause `SelfCustodyCandidate` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `SelfCustodyCandidate` (type)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `SelfCustodyCandidate`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `SelfCustodyCandidate` error paths asserting no biometric bytes appear in output.
