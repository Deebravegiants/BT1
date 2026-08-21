# Q2281: Deserialization boundary in spawn_thread lacks a size cap (agent/thread.rs)

## Question
Can an unprivileged attacker cause `spawn_thread` in [agentwire/src/agent/thread.rs](agentwire/src/agent/thread.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [agentwire/src/agent/thread.rs](agentwire/src/agent/thread.rs) -> `spawn_thread` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `spawn_thread` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `spawn_thread` with oversized length headers asserting the cap is enforced.
