# Q0059: Parser panic in parse_output reachable from a scanned payload (wpa-supplicant-interface/signal.rs)

## Question
Can an unprivileged attacker craft a QR payload that causes `parse_output` in [wpa-supplicant-interface/src/signal.rs](wpa-supplicant-interface/src/signal.rs) to panic, slice out of bounds, or recurse without bound, aborting the process or its parsing task while a signup is in flight?

## Target
- File/function: [wpa-supplicant-interface/src/signal.rs](wpa-supplicant-interface/src/signal.rs) -> `parse_output` (function)
- Entrypoint: Scanned QR payload
- Attacker controls: byte-level structure: truncation points, nesting depth, repeated separators
- Exploit idea: Fuzz around slicing/indexing and nested combinator paths in `parse_output`, especially at multi-byte UTF-8 boundaries.
- Invariant to test: `parse_output` is total over arbitrary bytes: it returns an error and never panics or unwinds.
- Expected Immunefi impact: Repeatable crash-loop leaving the Orb unable to complete signups
- Fast validation: cargo-fuzz / proptest harness on `parse_output` over arbitrary `&[u8]` asserting no panic.
