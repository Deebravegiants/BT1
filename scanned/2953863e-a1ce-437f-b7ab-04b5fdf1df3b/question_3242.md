# Q3242: Serialization round-trip in upload_all_signup_images is not faithful (agents/image_uploader.rs)

## Question
Can an unprivileged attacker supply data whose round-trip through `upload_all_signup_images` in [src/agents/image_uploader.rs](src/agents/image_uploader.rs) is lossy or non-injective (float precision, array shape, map ordering, truncation), so the stored/uploaded record differs from the validated one?

## Target
- File/function: [src/agents/image_uploader.rs](src/agents/image_uploader.rs) -> `upload_all_signup_images` (function)
- Entrypoint: Capture or payload content shaping the serialized values
- Attacker controls: numeric ranges, array shapes, and string content entering serialization
- Exploit idea: Property-test round-trips through `upload_all_signup_images` for values at type boundaries.
- Invariant to test: Serialization is lossless and injective for all in-range values.
- Expected Immunefi impact: Uploaded biometric record diverging from the validated capture
- Fast validation: Round-trip property test over `upload_all_signup_images` asserting equality for all generated values.
