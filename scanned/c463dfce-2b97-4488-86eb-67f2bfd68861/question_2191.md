# Q2191: Serialization round-trip in make_dist_coeffs is not faithful (image/fisheye.rs)

## Question
Can an unprivileged attacker supply data whose round-trip through `make_dist_coeffs` in [src/image/fisheye.rs](src/image/fisheye.rs) is lossy or non-injective (float precision, array shape, map ordering, truncation), so the stored/uploaded record differs from the validated one?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `make_dist_coeffs` (function)
- Entrypoint: Capture or payload content shaping the serialized values
- Attacker controls: numeric ranges, array shapes, and string content entering serialization
- Exploit idea: Property-test round-trips through `make_dist_coeffs` for values at type boundaries.
- Invariant to test: Serialization is lossless and injective for all in-range values.
- Expected Immunefi impact: Uploaded biometric record diverging from the validated capture
- Fast validation: Round-trip property test over `make_dist_coeffs` asserting equality for all generated values.
