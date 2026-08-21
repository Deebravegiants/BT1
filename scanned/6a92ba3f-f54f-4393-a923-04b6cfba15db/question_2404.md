# Q2404: Parser panic in main reachable from a scanned payload (orb-backend-connect/main.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `main` in [orb-backend-connect/src/main.rs](orb-backend-connect/src/main.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [orb-backend-connect/src/main.rs](orb-backend-connect/src/main.rs) -> `main` (function)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `main`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `main` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `main` over arbitrary `&[u8]` asserting no panic.
