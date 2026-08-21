# Q1883: TLS/authenticity of the request path in PersonalCustodyPackages (plans/personal_custody_package.rs)

## Question
Can an unprivileged attacker exploit `PersonalCustodyPackages` in [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) constructing a request whose scheme/host is assembled from data rather than pinned constants, so a data-driven value downgrades or redirects an authenticated biometric upload?

## Target
- File/function: [src/plans/personal_custody_package.rs](src/plans/personal_custody_package.rs) -> `PersonalCustodyPackages` (type)
- Entrypoint: Data fields that flow into endpoint construction
- Attacker controls: the endpoint-composing fields reachable from their session
- Exploit idea: Check `PersonalCustodyPackages` for constant scheme/host and enforced TLS.
- Invariant to test: Scheme and host are compile-time constants; only path/query may vary and only from validated values.
- Expected Immunefi impact: Biometric upload sent over an attacker-influenced channel
- Fast validation: Unit-test `PersonalCustodyPackages` asserting scheme/host are invariant across all inputs.
