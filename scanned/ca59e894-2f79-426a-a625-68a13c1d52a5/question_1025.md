# Q1025: Serialization round-trip in log_iris_data is not faithful (utils/mod.rs)

## Question
Can an unprivileged attacker supply data whose round-trip through `log_iris_data` in [src/utils/mod.rs](src/utils/mod.rs) is lossy or non-injective (float precision, array shape, map ordering, truncation), so the stored/uploaded record differs from the validated one?

## Target
- File/function: [src/utils/mod.rs](src/utils/mod.rs) -> `log_iris_data` (function)
- Entrypoint: Capture or payload content shaping the serialized values
- Attacker controls: numeric ranges, array shapes, and string content entering serialization
- Exploit idea: Property-test round-trips through `log_iris_data` for values at type boundaries.
- Invariant to test: Serialization is lossless and injective for all in-range values.
- Expected Immunefi impact: Uploaded biometric record diverging from the validated capture
- Fast validation: Round-trip property test over `log_iris_data` asserting equality for all generated values.
