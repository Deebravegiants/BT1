# Q3624: Deserialization boundary in operator_timestamp lacks a size cap (plans/mod.rs)

## Question
Can an unprivileged attacker cause `operator_timestamp` in [src/plans/mod.rs](src/plans/mod.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `operator_timestamp` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `operator_timestamp` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `operator_timestamp` with oversized length headers asserting the cap is enforced.
