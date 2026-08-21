# Q0202: Deserialization boundary in stop_depth_camera lacks a size cap (brokers/orb.rs)

## Question
Can an unprivileged attacker cause `stop_depth_camera` in [src/brokers/orb.rs](src/brokers/orb.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `stop_depth_camera` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `stop_depth_camera` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `stop_depth_camera` with oversized length headers asserting the cap is enforced.
