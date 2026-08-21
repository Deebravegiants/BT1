# Q2982: Raw biometric tensors leaked by user_distance (python/rgb_net.rs)

## Question
Can an unprivileged attacker cause `user_distance` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `user_distance` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `user_distance`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `user_distance` error paths asserting no biometric bytes appear in output.
