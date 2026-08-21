# Q3547: Parser panic in status reachable from a scanned payload (network/mod.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `status` in [src/network/mod.rs](src/network/mod.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [src/network/mod.rs](src/network/mod.rs) -> `status` (function)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `status`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `status` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `status` over arbitrary `&[u8]` asserting no panic.
