# Q2888: Raw biometric tensors leaked by run_python_process (python/mod.rs)

## Question
Can an unprivileged attacker cause `run_python_process` in [src/agents/python/mod.rs](src/agents/python/mod.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `run_python_process` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `run_python_process`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `run_python_process` error paths asserting no biometric bytes appear in output.
