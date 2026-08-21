# Q2346: Parser panic in handle_qr_code reachable from a scanned payload (qr_scan/mod.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `handle_qr_code` in [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [src/plans/qr_scan/mod.rs](src/plans/qr_scan/mod.rs) -> `handle_qr_code` (function)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `handle_qr_code`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `handle_qr_code` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `handle_qr_code` over arbitrary `&[u8]` asserting no panic.
