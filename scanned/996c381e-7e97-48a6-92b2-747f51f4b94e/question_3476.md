# Q3476: Deserialization boundary in Event lacks a size cap (livestream-event/lib.rs)

## Question
Can an unprivileged attacker cause `Event` in [livestream-event/src/lib.rs](livestream-event/src/lib.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [livestream-event/src/lib.rs](livestream-event/src/lib.rs) -> `Event` (type)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `Event` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `Event` with oversized length headers asserting the cap is enforced.
