# Q1035: Serialization round-trip in serialize is not faithful (utils/serializable_instant.rs)

## Question
Can an unprivileged attacker supply data whose round-trip through `serialize` in [src/utils/serializable_instant.rs](src/utils/serializable_instant.rs) is lossy or non-injective (float precision, array shape, map ordering, truncation), so the stored/uploaded record differs from the validated one?

## Target
- File/function: [src/utils/serializable_instant.rs](src/utils/serializable_instant.rs) -> `serialize` (function)
- Entrypoint: Capture or payload content shaping the serialized values
- Attacker controls: numeric ranges, array shapes, and string content entering serialization
- Exploit idea: Property-test round-trips through `serialize` for values at type boundaries.
- Invariant to test: Serialization is lossless and injective for all in-range values.
- Expected Immunefi impact: Uploaded biometric record diverging from the validated capture
- Fast validation: Round-trip property test over `serialize` asserting equality for all generated values.
