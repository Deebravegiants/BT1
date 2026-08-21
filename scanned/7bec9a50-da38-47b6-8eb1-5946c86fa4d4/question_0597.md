# Q0597: Raw biometric tensors leaked by Triplet (face_identifier/types.rs)

## Question
Can an unprivileged attacker cause `Triplet` in [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) -> `Triplet` (type)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `Triplet`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `Triplet` error paths asserting no biometric bytes appear in output.
