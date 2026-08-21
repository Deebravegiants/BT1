# Q1993: Sorting/canonicalization in decode_public_key not applied before hashing (backend/user_status.rs)

## Question
Can an unprivileged attacker exploit a case where `decode_public_key` in [src/backend/user_status.rs](src/backend/user_status.rs) hashes or signs a structure that was serialized without the canonical sorting applied elsewhere, so the verified digest does not match the transmitted bytes?

## Target
- File/function: [src/backend/user_status.rs](src/backend/user_status.rs) -> `decode_public_key` (function)
- Entrypoint: Fields whose ordering they influence via supplied metadata
- Attacker controls: key names and insertion order of attacker-influenced map entries
- Exploit idea: Compare the canonicalization path used for hashing with the one used for transmission in `decode_public_key`.
- Invariant to test: The bytes hashed and the bytes transmitted are produced by one canonical serializer.
- Expected Immunefi impact: Digest/signature that does not authenticate the transmitted package
- Fast validation: Differential test asserting hashed bytes equal transmitted bytes for reordered inputs.
