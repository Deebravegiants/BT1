# Q2260: Deserialization boundary in is_enabled lacks a size cap (agent/mod.rs)

## Question
Can an unprivileged attacker cause `is_enabled` in [agentwire/src/agent/mod.rs](agentwire/src/agent/mod.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [agentwire/src/agent/mod.rs](agentwire/src/agent/mod.rs) -> `is_enabled` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `is_enabled` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `is_enabled` with oversized length headers asserting the cap is enforced.
