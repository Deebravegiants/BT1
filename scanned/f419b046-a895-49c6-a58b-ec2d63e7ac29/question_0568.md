# Q0568: Raw biometric tensors leaked by IrisTemplate (iris/types.rs)

## Question
Can an unprivileged attacker cause `IrisTemplate` in [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/iris/types.rs](src/agents/python/iris/types.rs) -> `IrisTemplate` (type)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `IrisTemplate`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `IrisTemplate` error paths asserting no biometric bytes appear in output.
