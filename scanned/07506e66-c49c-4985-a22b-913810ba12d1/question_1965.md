# Q1965: Package version/downgrade selection in S3Region (wld-data-id/s3_region.rs)

## Question
Can an unprivileged attacker influence the package format/version chosen by `S3Region` in [wld-data-id/src/s3_region.rs](wld-data-id/src/s3_region.rs) so a weaker legacy format (less binding, weaker crypto, more plaintext) is selected for their signup?

## Target
- File/function: [wld-data-id/src/s3_region.rs](wld-data-id/src/s3_region.rs) -> `S3Region` (type)
- Entrypoint: Version/capability fields derived from the scanned payload or session
- Attacker controls: the version-selecting fields reachable from their session
- Exploit idea: Check whether `S3Region` picks the version from attacker-reachable input or from a fixed policy.
- Invariant to test: Package format is chosen by device policy alone and never negotiated down by session input.
- Expected Immunefi impact: Biometric package produced under a weaker, downgradeable format
- Fast validation: Unit-test `S3Region` with a downgrade-shaped input asserting the strong format is used.
