# Q0997: Sorting/canonicalization in log_to_file not applied before hashing (logger.rs)

## Question
Can an unprivileged attacker exploit a case where `log_to_file` in [src/logger.rs](src/logger.rs) hashes or signs a structure that was serialized without the canonical sorting applied elsewhere, so the verified digest does not match the transmitted bytes?

## Target
- File/function: [src/logger.rs](src/logger.rs) -> `log_to_file` (function)
- Entrypoint: Fields whose ordering they influence via supplied metadata
- Attacker controls: key names and insertion order of attacker-influenced map entries
- Exploit idea: Compare the canonicalization path used for hashing with the one used for transmission in `log_to_file`.
- Invariant to test: The bytes hashed and the bytes transmitted are produced by one canonical serializer.
- Expected Immunefi impact: Digest/signature that does not authenticate the transmitted package
- Fast validation: Differential test asserting hashed bytes equal transmitted bytes for reordered inputs.
