# Q2591: Deserialization boundary in StateRx lacks a size cap (brokers/orb.rs)

## Question
Can an unprivileged attacker cause `StateRx` in [src/brokers/orb.rs](src/brokers/orb.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `StateRx` (type)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `StateRx` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `StateRx` with oversized length headers asserting the cap is enforced.
