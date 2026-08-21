# Q1077: Deserialization boundary in CreateSharedMemoryError lacks a size cap (agentwire/port.rs)

## Question
Can an unprivileged attacker cause `CreateSharedMemoryError` in [agentwire/src/port.rs](agentwire/src/port.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [agentwire/src/port.rs](agentwire/src/port.rs) -> `CreateSharedMemoryError` (type)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `CreateSharedMemoryError` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `CreateSharedMemoryError` with oversized length headers asserting the cap is enforced.
