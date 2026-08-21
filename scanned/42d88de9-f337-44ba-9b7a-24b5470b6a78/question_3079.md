# Q3079: Package version/downgrade selection in read_hardware_version (identification.rs)

## Question
Can an unprivileged attacker influence the package format/version chosen by `read_hardware_version` in [src/identification.rs](src/identification.rs) so a weaker legacy format (less binding, weaker crypto, more plaintext) is selected for their signup?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `read_hardware_version` (function)
- Entrypoint: Version/capability fields derived from the scanned payload or session
- Attacker controls: the version-selecting fields reachable from their session
- Exploit idea: Check whether `read_hardware_version` picks the version from attacker-reachable input or from a fixed policy.
- Invariant to test: Package format is chosen by device policy alone and never negotiated down by session input.
- Expected Immunefi impact: Biometric package produced under a weaker, downgradeable format
- Fast validation: Unit-test `read_hardware_version` with a downgrade-shaped input asserting the strong format is used.
