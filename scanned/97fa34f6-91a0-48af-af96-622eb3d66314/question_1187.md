# Q1187: Sorting/canonicalization in from_signup_extension not applied before hashing (qr_scan/user.rs)

## Question
Can an unprivileged attacker exploit a case where `from_signup_extension` in [src/plans/qr_scan/user.rs](src/plans/qr_scan/user.rs) hashes or signs a structure that was serialized without the canonical sorting applied elsewhere, so the verified digest does not match the transmitted bytes?

## Target
- File/function: [src/plans/qr_scan/user.rs](src/plans/qr_scan/user.rs) -> `from_signup_extension` (function)
- Entrypoint: Fields whose ordering they influence via supplied metadata
- Attacker controls: key names and insertion order of attacker-influenced map entries
- Exploit idea: Compare the canonicalization path used for hashing with the one used for transmission in `from_signup_extension`.
- Invariant to test: The bytes hashed and the bytes transmitted are produced by one canonical serializer.
- Expected Immunefi impact: Digest/signature that does not authenticate the transmitted package
- Fast validation: Differential test asserting hashed bytes equal transmitted bytes for reordered inputs.
