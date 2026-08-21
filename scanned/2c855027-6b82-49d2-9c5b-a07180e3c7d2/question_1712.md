# Q1712: Raw biometric tensors leaked by choose_config (python/mod.rs)

## Question
Can an unprivileged attacker cause `choose_config` in [src/agents/python/mod.rs](src/agents/python/mod.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `choose_config` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `choose_config`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `choose_config` error paths asserting no biometric bytes appear in output.
