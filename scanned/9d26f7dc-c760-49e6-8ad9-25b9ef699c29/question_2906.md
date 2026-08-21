# Q2906: Raw biometric tensors leaked by serialized_image (iris/types.rs)

## Question
Can an unprivileged attacker cause `serialized_image` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `serialized_image` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `serialized_image`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `serialized_image` error paths asserting no biometric bytes appear in output.
