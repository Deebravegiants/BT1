# Q2062: Package version/downgrade selection in Queue (agents/data_uploader.rs)

## Question
Can an unprivileged attacker influence the package format/version chosen by `Queue` in [src/agents/data_uploader.rs](src/agents/data_uploader.rs) so a weaker legacy format (less binding, weaker crypto, more plaintext) is selected for their signup?

## Target
- File/function: [src/agents/data_uploader.rs](src/agents/data_uploader.rs) -> `Queue` (type)
- Entrypoint: Version/capability fields derived from the scanned payload or session
- Attacker controls: the version-selecting fields reachable from their session
- Exploit idea: Check whether `Queue` picks the version from attacker-reachable input or from a fixed policy.
- Invariant to test: Package format is chosen by device policy alone and never negotiated down by session input.
- Expected Immunefi impact: Biometric package produced under a weaker, downgradeable format
- Fast validation: Unit-test `Queue` with a downgrade-shaped input asserting the strong format is used.
