# Q0723: Package version/downgrade selection in get_public_pem (secure_element.rs)

## Question
Can an unprivileged attacker influence the package format/version chosen by `get_public_pem` in [src/secure_element.rs](src/secure_element.rs) so a weaker legacy format (less binding, weaker crypto, more plaintext) is selected for their signup?

## Target
- File/function: [src/secure_element.rs](src/secure_element.rs) -> `get_public_pem` (function)
- Entrypoint: Version/capability fields derived from the scanned payload or session
- Attacker controls: the version-selecting fields reachable from their session
- Exploit idea: Check whether `get_public_pem` picks the version from attacker-reachable input or from a fixed policy.
- Invariant to test: Package format is chosen by device policy alone and never negotiated down by session input.
- Expected Immunefi impact: Biometric package produced under a weaker, downgradeable format
- Fast validation: Unit-test `get_public_pem` with a downgrade-shaped input asserting the strong format is used.
