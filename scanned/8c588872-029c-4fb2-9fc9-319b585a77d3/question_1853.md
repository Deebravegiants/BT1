# Q1853: Raw biometric tensors leaked by estimate (ir-net/lib.rs)

## Question
Can an unprivileged attacker cause `estimate` in [ir-net/src/lib.rs](ir-net/src/lib.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [ir-net/src/lib.rs](ir-net/src/lib.rs) -> `estimate` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `estimate`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `estimate` error paths asserting no biometric bytes appear in output.
