# Q3551: Parser panic in wpa_passphrase reachable from a scanned payload (network/mod.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `wpa_passphrase` in [src/network/mod.rs](src/network/mod.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [src/network/mod.rs](src/network/mod.rs) -> `wpa_passphrase` (function)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `wpa_passphrase`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `wpa_passphrase` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `wpa_passphrase` over arbitrary `&[u8]` asserting no panic.
