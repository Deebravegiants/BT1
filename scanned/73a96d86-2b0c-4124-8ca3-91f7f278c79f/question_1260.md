# Q1260: Deserialization boundary in scan_operator_qr_code lacks a size cap (plans/mod.rs)

## Question
Can an unprivileged attacker cause `scan_operator_qr_code` in [src/plans/mod.rs](src/plans/mod.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `scan_operator_qr_code` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `scan_operator_qr_code` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `scan_operator_qr_code` with oversized length headers asserting the cap is enforced.
