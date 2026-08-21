# Q2607: Deserialization boundary in is_fan_control_active lacks a size cap (brokers/observer.rs)

## Question
Can an unprivileged attacker cause `is_fan_control_active` in [src/brokers/observer.rs](src/brokers/observer.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/brokers/observer.rs](src/brokers/observer.rs) -> `is_fan_control_active` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `is_fan_control_active` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `is_fan_control_active` with oversized length headers asserting the cap is enforced.
