# Q0298: Deserialization boundary in Builder lacks a size cap (brokers/observer.rs)

## Question
Can an unprivileged attacker cause `Builder` in [src/brokers/observer.rs](src/brokers/observer.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `Builder` (type)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `Builder` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `Builder` with oversized length headers asserting the cap is enforced.
