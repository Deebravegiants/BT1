# Q0728: Package version/downgrade selection in set_jabil_id (identification.rs)

## Question
Can an unprivileged attacker influence the package format/version chosen by `set_jabil_id` in [src/identification.rs](src/identification.rs) so a weaker legacy format (less binding, weaker crypto, more plaintext) is selected for their signup?

## Target
- File/function: [src/identification.rs](src/identification.rs) -> `set_jabil_id` (function)
- Entrypoint: Version/capability fields derived from the scanned payload or session
- Attacker controls: the version-selecting fields reachable from their session
- Exploit idea: Check whether `set_jabil_id` picks the version from attacker-reachable input or from a fixed policy.
- Invariant to test: Package format is chosen by device policy alone and never negotiated down by session input.
- Expected Immunefi impact: Biometric package produced under a weaker, downgradeable format
- Fast validation: Unit-test `set_jabil_id` with a downgrade-shaped input asserting the strong format is used.
