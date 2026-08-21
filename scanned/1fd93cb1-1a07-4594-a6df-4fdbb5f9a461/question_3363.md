# Q3363: Sorting/canonicalization in make_dist_coeffs not applied before hashing (image/fisheye.rs)

## Question
Can an unprivileged attacker exploit a case where `make_dist_coeffs` in [src/image/fisheye.rs](src/image/fisheye.rs) hashes or signs a structure that was serialized without the canonical sorting applied elsewhere, so the verified digest does not match the transmitted bytes?

## Target
- File/function: [src/image/fisheye.rs](src/image/fisheye.rs) -> `make_dist_coeffs` (function)
- Entrypoint: Fields whose ordering they influence via supplied metadata
- Attacker controls: key names and insertion order of attacker-influenced map entries
- Exploit idea: Compare the canonicalization path used for hashing with the one used for transmission in `make_dist_coeffs`.
- Invariant to test: The bytes hashed and the bytes transmitted are produced by one canonical serializer.
- Expected Immunefi impact: Digest/signature that does not authenticate the transmitted package
- Fast validation: Differential test asserting hashed bytes equal transmitted bytes for reordered inputs.
