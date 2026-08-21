# Q1736: Raw biometric tensors leaked by serialized_image_and_mask (iris/types.rs)

## Question
Can an unprivileged attacker cause `serialized_image_and_mask` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `serialized_image_and_mask` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `serialized_image_and_mask`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `serialized_image_and_mask` error paths asserting no biometric bytes appear in output.
