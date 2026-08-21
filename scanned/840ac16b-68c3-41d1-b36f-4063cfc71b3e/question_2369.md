# Q2369: Parser panic in exit_strategy reachable from a scanned payload (agents/qr_code.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `exit_strategy` in [src/agents/qr_code.rs](src/agents/qr_code.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [src/agents/qr_code.rs](src/agents/qr_code.rs) -> `exit_strategy` (function)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `exit_strategy`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `exit_strategy` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `exit_strategy` over arbitrary `&[u8]` asserting no panic.
