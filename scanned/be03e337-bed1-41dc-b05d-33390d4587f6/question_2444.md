# Q2444: Deserialization boundary in ui_complete_signup lacks a size cap (plans/mod.rs)

## Question
Can an unprivileged attacker cause `ui_complete_signup` in [src/plans/mod.rs](src/plans/mod.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `ui_complete_signup` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `ui_complete_signup` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `ui_complete_signup` with oversized length headers asserting the cap is enforced.
