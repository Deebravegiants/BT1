# Q0038: Parser panic in parse reachable from a scanned payload (network/mecard.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `parse` in [src/network/mecard.rs](src/network/mecard.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [src/network/mecard.rs](src/network/mecard.rs) -> `parse` (function)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `parse`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `parse` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `parse` over arbitrary `&[u8]` asserting no panic.
