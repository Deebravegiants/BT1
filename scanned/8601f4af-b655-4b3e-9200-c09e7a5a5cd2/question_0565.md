# Q0565: Raw biometric tensors leaked by extract_maskcode_hist (iris/types.rs)

## Question
Can an unprivileged attacker cause `extract_maskcode_hist` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `extract_maskcode_hist` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `extract_maskcode_hist`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `extract_maskcode_hist` error paths asserting no biometric bytes appear in output.
