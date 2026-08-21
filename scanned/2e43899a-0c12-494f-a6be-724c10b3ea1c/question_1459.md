# Q1459: Deserialization boundary in ssd_health_check lacks a size cap (brokers/observer.rs)

## Question
Can an unprivileged attacker cause `ssd_health_check` in [src/brokers/observer.rs](src/brokers/observer.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `ssd_health_check` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `ssd_health_check` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `ssd_health_check` with oversized length headers asserting the cap is enforced.
