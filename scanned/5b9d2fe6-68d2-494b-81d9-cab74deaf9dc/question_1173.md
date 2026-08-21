# Q1173: Parser panic in try_parse reachable from a scanned payload (qr_scan/mod.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `try_parse` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `try_parse` (function)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `try_parse`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `try_parse` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `try_parse` over arbitrary `&[u8]` asserting no panic.
