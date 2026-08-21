# Q0576: Raw biometric tensors leaked by iterate (face_identifier/mod.rs)

## Question
Can an unprivileged attacker cause `iterate` in [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) -> `iterate` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `iterate`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `iterate` error paths asserting no biometric bytes appear in output.
