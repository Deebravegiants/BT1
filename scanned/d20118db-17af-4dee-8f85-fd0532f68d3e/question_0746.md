# Q0746: Package version/downgrade selection in save_identification_images (agents/image_notary.rs)

## Question
Can an unprivileged attacker influence the package format/version chosen by `save_identification_images` in [src/agents/image_notary.rs](src/agents/image_notary.rs) so a weaker legacy format (less binding, weaker crypto, more plaintext) is selected for their signup?

## Target
- File/function: [src/agents/image_notary.rs](src/agents/image_notary.rs) -> `save_identification_images` (function)
- Entrypoint: Version/capability fields derived from the scanned payload or session
- Attacker controls: the version-selecting fields reachable from their session
- Exploit idea: Check whether `save_identification_images` picks the version from attacker-reachable input or from a fixed policy.
- Invariant to test: Package format is chosen by device policy alone and never negotiated down by session input.
- Expected Immunefi impact: Biometric package produced under a weaker, downgradeable format
- Fast validation: Unit-test `save_identification_images` with a downgrade-shaped input asserting the strong format is used.
