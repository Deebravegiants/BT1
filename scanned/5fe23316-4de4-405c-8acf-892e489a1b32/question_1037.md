# Q1037: Sorting/canonicalization in sorted_keys not applied before hashing (utils/serialize_with_sorted_keys.rs)

## Question
Can an unprivileged attacker exploit a case where `sorted_keys` in [src/utils/serialize_with_sorted_keys.rs](src/utils/serialize_with_sorted_keys.rs) hashes or signs a structure that was serialized without the canonical sorting applied elsewhere, so the verified digest does not match the transmitted bytes?

## Target
- File/function: [src/utils/serialize_with_sorted_keys.rs](src/utils/serialize_with_sorted_keys.rs) -> `sorted_keys` (function)
- Entrypoint: Fields whose ordering they influence via supplied metadata
- Attacker controls: key names and insertion order of attacker-influenced map entries
- Exploit idea: Compare the canonicalization path used for hashing with the one used for transmission in `sorted_keys`.
- Invariant to test: The bytes hashed and the bytes transmitted are produced by one canonical serializer.
- Expected Immunefi impact: Digest/signature that does not authenticate the transmitted package
- Fast validation: Differential test asserting hashed bytes equal transmitted bytes for reordered inputs.
