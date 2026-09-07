# [M] Pimcore Demo Allows GraphQL Introspection

## Summary
Severity: Medium
Advisory: GHSA-p76j-h4m8-hx5c
CVE: CVE-2023-5192
CWE: CWE-1049, CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2023-09-27
Source: https://github.com/advisories/GHSA-p76j-h4m8-hx5c
Type: github-advisory

## Affected
- Packagist: `pimcore/demo` — affected >=0 <10.3.0

## Details
Introspection is enabled on `demo.pimcore.fun`. The demo site has graphql as a feature for users, but allows users to run instropection queries, which presents a potential schema information disclosure vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5192
- https://github.com/pimcore/demo/pull/437
- https://github.com/pimcore/demo/commit/a2a7ff3b565882aefb759804aac4a51afb458f1f
- https://github.com/pimcore/demo
- https://huntr.dev/bounties/65c954f2-79c3-4672-8846-a3035e7a1db7
