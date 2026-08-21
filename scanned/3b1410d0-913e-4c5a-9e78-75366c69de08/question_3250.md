# Q3250: Sorting/canonicalization in biometric_capture_succeeded not applied before hashing (debug_report.rs)

## Question
Can an unprivileged attacker exploit a case where `biometric_capture_succeeded` in [src/debug_report.rs](src/debug_report.rs) hashes or signs a structure that was serialized without the canonical sorting applied elsewhere, so the verified digest does not match the transmitted bytes?

## Target
- File/function: [src/debug_report.rs](src/debug_report.rs) -> `biometric_capture_succeeded` (function)
- Entrypoint: Fields whose ordering they influence via supplied metadata
- Attacker controls: key names and insertion order of attacker-influenced map entries
- Exploit idea: Compare the canonicalization path used for hashing with the one used for transmission in `biometric_capture_succeeded`.
- Invariant to test: The bytes hashed and the bytes transmitted are produced by one canonical serializer.
- Expected Immunefi impact: Digest/signature that does not authenticate the transmitted package
- Fast validation: Differential test asserting hashed bytes equal transmitted bytes for reordered inputs.
