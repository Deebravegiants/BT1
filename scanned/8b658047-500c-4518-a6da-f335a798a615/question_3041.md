# Q3041: Package version/downgrade selection in make_iris_codes_json (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker influence the package format/version chosen by `make_iris_codes_json` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) so a weaker legacy format (less binding, weaker crypto, more plaintext) is selected for their signup?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `make_iris_codes_json` (function)
- Entrypoint: Version/capability fields derived from the scanned payload or session
- Attacker controls: the version-selecting fields reachable from their session
- Exploit idea: Check whether `make_iris_codes_json` picks the version from attacker-reachable input or from a fixed policy.
- Invariant to test: Package format is chosen by device policy alone and never negotiated down by session input.
- Expected Immunefi impact: Biometric package produced under a weaker, downgradeable format
- Fast validation: Unit-test `make_iris_codes_json` with a downgrade-shaped input asserting the strong format is used.
