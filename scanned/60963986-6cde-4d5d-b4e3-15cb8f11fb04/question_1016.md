# Q1016: Serialization round-trip in scale_camera_matrix is not faithful (image/fisheye.rs)

## Question
Can an unprivileged attacker supply data whose round-trip through `scale_camera_matrix` in [src/image/fisheye.rs](src/image/fisheye.rs) is lossy or non-injective (float precision, array shape, map ordering, truncation), so the stored/uploaded record differs from the validated one?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `scale_camera_matrix` (function)
- Entrypoint: Capture or payload content shaping the serialized values
- Attacker controls: numeric ranges, array shapes, and string content entering serialization
- Exploit idea: Property-test round-trips through `scale_camera_matrix` for values at type boundaries.
- Invariant to test: Serialization is lossless and injective for all in-range values.
- Expected Immunefi impact: Uploaded biometric record diverging from the validated capture
- Fast validation: Round-trip property test over `scale_camera_matrix` asserting equality for all generated values.
