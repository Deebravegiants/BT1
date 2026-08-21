# Q3238: Sorting/canonicalization in upload_image not applied before hashing (agents/image_uploader.rs)

## Question
Can an unprivileged attacker exploit a case where `upload_image` in [src/agents/image_uploader.rs](src/agents/image_uploader.rs) hashes or signs a structure that was serialized without the canonical sorting applied elsewhere, so the verified digest does not match the transmitted bytes?

## Target
- File/function: [src/agents/image_uploader.rs](src/agents/image_uploader.rs) -> `upload_image` (function)
- Entrypoint: Fields whose ordering they influence via supplied metadata
- Attacker controls: key names and insertion order of attacker-influenced map entries
- Exploit idea: Compare the canonicalization path used for hashing with the one used for transmission in `upload_image`.
- Invariant to test: The bytes hashed and the bytes transmitted are produced by one canonical serializer.
- Expected Immunefi impact: Digest/signature that does not authenticate the transmitted package
- Fast validation: Differential test asserting hashed bytes equal transmitted bytes for reordered inputs.
