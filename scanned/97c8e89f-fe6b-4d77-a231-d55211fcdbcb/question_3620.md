# Q3620: Deserialization boundary in build_pcp lacks a size cap (plans/mod.rs)

## Question
Can an unprivileged attacker cause `build_pcp` in [src/plans/mod.rs](src/plans/mod.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `build_pcp` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `build_pcp` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `build_pcp` with oversized length headers asserting the cap is enforced.
