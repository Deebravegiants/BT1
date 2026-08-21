# Q0665: Raw biometric tensors leaked by fusion_rgb_net_face_identifier (python/mega_agent_two.rs)

## Question
Can an unprivileged attacker cause `fusion_rgb_net_face_identifier` in [src/agents/python/mega_agent_two.rs](src/agents/python/mega_agent_two.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/mega_agent_two.rs](src/agents/python/mega_agent_two.rs) -> `fusion_rgb_net_face_identifier` (function)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `fusion_rgb_net_face_identifier`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `fusion_rgb_net_face_identifier` error paths asserting no biometric bytes appear in output.
