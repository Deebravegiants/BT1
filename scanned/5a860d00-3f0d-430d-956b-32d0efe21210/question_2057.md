# Q2057: Serialization round-trip in drop_oldest is not faithful (agents/data_uploader.rs)

## Question
Can an unprivileged attacker supply data whose round-trip through `drop_oldest` in [src/agents/data_uploader.rs](src/agents/data_uploader.rs) is lossy or non-injective (float precision, array shape, map ordering, truncation), so the stored/uploaded record differs from the validated one?

## Target
- File/function: [src/agents/data_uploader.rs](src/agents/data_uploader.rs) -> `drop_oldest` (function)
- Entrypoint: Capture or payload content shaping the serialized values
- Attacker controls: numeric ranges, array shapes, and string content entering serialization
- Exploit idea: Property-test round-trips through `drop_oldest` for values at type boundaries.
- Invariant to test: Serialization is lossless and injective for all in-range values.
- Expected Immunefi impact: Uploaded biometric record diverging from the validated capture
- Fast validation: Round-trip property test over `drop_oldest` asserting equality for all generated values.
