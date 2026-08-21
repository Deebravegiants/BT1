# Q1235: Deserialization boundary in qr_scan_timeout lacks a size cap (plans/mod.rs)

## Question
Can an unprivileged attacker cause `qr_scan_timeout` in [src/plans/mod.rs](src/plans/mod.rs) to decode a message whose declared size is attacker-influenced and unbounded, allocating far beyond available memory?

## Target
- File/function: [src/plans/mod.rs](src/plans/mod.rs) -> `qr_scan_timeout` (function)
- Entrypoint: Data whose size flows from capture/scan into the message
- Attacker controls: the size-determining content of the input
- Exploit idea: Check `qr_scan_timeout` for a maximum message size enforced before allocation.
- Invariant to test: Message size limits are enforced before any allocation.
- Expected Immunefi impact: Memory exhaustion from routine attacker-shaped input
- Fast validation: Fuzz `qr_scan_timeout` with oversized length headers asserting the cap is enforced.
