# Q3248: Serialization round-trip in empty is not faithful (debug_report.rs)

## Question
Can an unprivileged attacker supply data whose round-trip through `empty` in [src/debug_report.rs](src/debug_report.rs) is lossy or non-injective (float precision, array shape, map ordering, truncation), so the stored/uploaded record differs from the validated one?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `empty` (function)
- Entrypoint: Capture or payload content shaping the serialized values
- Attacker controls: numeric ranges, array shapes, and string content entering serialization
- Exploit idea: Property-test round-trips through `empty` for values at type boundaries.
- Invariant to test: Serialization is lossless and injective for all in-range values.
- Expected Immunefi impact: Uploaded biometric record diverging from the validated capture
- Fast validation: Round-trip property test over `empty` asserting equality for all generated values.
