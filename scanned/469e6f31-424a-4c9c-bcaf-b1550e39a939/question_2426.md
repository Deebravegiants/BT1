# Q2426: Deserialization boundary in reset_hardware lacks a size cap (plans/mod.rs)

## Question
Can an unprivileged attacker cause `reset_hardware` in [src/plans/mod.rs](src/plans/mod.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `reset_hardware` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `reset_hardware` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `reset_hardware` with oversized length headers asserting the cap is enforced.
