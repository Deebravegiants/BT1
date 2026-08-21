# Q2199: Serialization round-trip in spawn_named_thread is not faithful (utils/mod.rs)

## Question
Can an unprivileged attacker supply data whose round-trip through `spawn_named_thread` in [src/utils/mod.rs](src/utils/mod.rs) is lossy or non-injective (float precision, array shape, map ordering, truncation), so the stored/uploaded record differs from the validated one?

## Target
- File/function: [src/utils/mod.rs](src/utils/mod.rs) -> `spawn_named_thread` (function)
- Entrypoint: Capture or payload content shaping the serialized values
- Attacker controls: numeric ranges, array shapes, and string content entering serialization
- Exploit idea: Property-test round-trips through `spawn_named_thread` for values at type boundaries.
- Invariant to test: Serialization is lossless and injective for all in-range values.
- Expected Immunefi impact: Uploaded biometric record diverging from the validated capture
- Fast validation: Round-trip property test over `spawn_named_thread` asserting equality for all generated values.
