# Q0603: Raw biometric tensors leaked by iterate (python/occlusion.rs)

## Question
Can an unprivileged attacker cause `iterate` in [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) -> `iterate` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `iterate`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `iterate` error paths asserting no biometric bytes appear in output.
