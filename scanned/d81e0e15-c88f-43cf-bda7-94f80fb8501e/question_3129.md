# Q3129: Package version/downgrade selection in from_image_path (wld-data-id/wld_data_id.rs)

## Question
Can an unprivileged attacker influence the package format/version chosen by `from_image_path` in [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) so a weaker legacy format (less binding, weaker crypto, more plaintext) is selected for their signup?

## Target
- File/function: [wld-data-id/src/wld_data_id.rs](wld-data-id/src/wld_data_id.rs) -> `from_image_path` (function)
- Entrypoint: Version/capability fields derived from the scanned payload or session
- Attacker controls: the version-selecting fields reachable from their session
- Exploit idea: Check whether `from_image_path` picks the version from attacker-reachable input or from a fixed policy.
- Invariant to test: Package format is chosen by device policy alone and never negotiated down by session input.
- Expected Immunefi impact: Biometric package produced under a weaker, downgradeable format
- Fast validation: Unit-test `from_image_path` with a downgrade-shaped input asserting the strong format is used.
