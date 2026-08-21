# Q2364: Parser panic in SignupMode reachable from a scanned payload (qr_scan/user.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `SignupMode` in [src/plans/qr_scan/user.rs](src/plans/qr_scan/user.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [src/plans/qr_scan/user.rs](src/plans/qr_scan/user.rs) -> `SignupMode` (type)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `SignupMode`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `SignupMode` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `SignupMode` over arbitrary `&[u8]` asserting no panic.
