# Q3571: Parser panic in run reachable from a scanned payload (wpa-supplicant-interface/status.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `run` in [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [wpa-supplicant-interface/src/status.rs](wpa-supplicant-interface/src/status.rs) -> `run` (function)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `run`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `run` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `run` over arbitrary `&[u8]` asserting no panic.
