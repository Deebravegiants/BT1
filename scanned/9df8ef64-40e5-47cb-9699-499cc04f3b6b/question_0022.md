# Q0022: Parser panic in Data reachable from a scanned payload (qr_scan/operator.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `Data` in [src/plans/qr_scan/operator.rs](src/plans/qr_scan/operator.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [src/plans/qr_scan/operator.rs](src/plans/qr_scan/operator.rs) -> `Data` (type)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `Data`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `Data` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `Data` over arbitrary `&[u8]` asserting no panic.
