# Q1394: Deserialization boundary in send_rgb_net_estimate lacks a size cap (brokers/orb.rs)

## Question
Can an unprivileged attacker cause `send_rgb_net_estimate` in [src/brokers/orb.rs](src/brokers/orb.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/brokers/orb.rs](src/brokers/orb.rs) -> `send_rgb_net_estimate` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `send_rgb_net_estimate` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `send_rgb_net_estimate` with oversized length headers asserting the cap is enforced.
