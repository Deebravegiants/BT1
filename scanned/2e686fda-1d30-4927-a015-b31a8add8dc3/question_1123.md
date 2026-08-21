# Q1123: Deserialization boundary in Upstream lacks a size cap (livestream/upstream.rs)

## Question
Can an unprivileged attacker cause `Upstream` in [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/agents/livestream/upstream.rs](src/agents/livestream/upstream.rs) -> `Upstream` (type)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `Upstream` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `Upstream` with oversized length headers asserting the cap is enforced.
