# Q1848: Raw biometric tensors leaked by from (ai-interface/lib.rs)

## Question
Can an unprivileged attacker cause `from` in [ai-interface/src/lib.rs](ai-interface/src/lib.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [ai-interface/src/lib.rs](ai-interface/src/lib.rs) -> `from` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `from`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `from` error paths asserting no biometric bytes appear in output.
