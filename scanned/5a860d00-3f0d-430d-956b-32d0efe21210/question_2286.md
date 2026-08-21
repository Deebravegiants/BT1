# Q2286: Deserialization boundary in encrypt_and_seal lacks a size cap (agents/mod.rs)

## Question
Can an unprivileged attacker cause `encrypt_and_seal` in [src/agents/mod.rs](src/agents/mod.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/agents/mod.rs](src/agents/mod.rs) -> `encrypt_and_seal` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `encrypt_and_seal` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `encrypt_and_seal` with oversized length headers asserting the cap is enforced.
