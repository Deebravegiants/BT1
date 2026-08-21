# Q0913: Serialization round-trip in enrollment_status is not faithful (debug_report.rs)

## Question
Can an unprivileged attacker supply data whose round-trip through `enrollment_status` in [src/debug_report.rs](src/debug_report.rs) is lossy or non-injective (float precision, array shape, map ordering, truncation), so the stored/uploaded record differs from the validated one?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `enrollment_status` (function)
- Entrypoint: Capture or payload content shaping the serialized values
- Attacker controls: numeric ranges, array shapes, and string content entering serialization
- Exploit idea: Property-test round-trips through `enrollment_status` for values at type boundaries.
- Invariant to test: Serialization is lossless and injective for all in-range values.
- Expected Immunefi impact: Uploaded biometric record diverging from the validated capture
- Fast validation: Round-trip property test over `enrollment_status` asserting equality for all generated values.
