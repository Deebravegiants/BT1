# Q1832: Raw biometric tensors leaked by MegaAgentOne (python/mega_agent_one.rs)

## Question
Can an unprivileged attacker cause `MegaAgentOne` in [src/agents/python/mega_agent_one.rs](src/agents/python/mega_agent_one.rs) to write raw biometric tensors/embeddings (iris codes, face embeddings) into logs, debug artifacts, or error strings that leave the Orb's protected storage?

## Target
- File/function: [src/agents/python/mega_agent_one.rs](src/agents/python/mega_agent_one.rs) -> `MegaAgentOne` (type)
- Entrypoint: Inducing the error/debug path during a signup
- Attacker controls: conditions that force the error/serialization branch
- Exploit idea: Trace `MegaAgentOne`'s error and Debug formatting for inclusion of biometric arrays.
- Invariant to test: Biometric arrays are never rendered into logs, errors, or debug artifacts.
- Expected Immunefi impact: Disclosure of raw biometric material
- Fast validation: Unit-test `MegaAgentOne` error paths asserting no biometric bytes appear in output.
