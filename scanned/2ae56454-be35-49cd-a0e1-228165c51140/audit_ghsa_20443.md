# [M] archivy is vulnerable to Cross-Site Request Forgery (CSRF)

## Summary
Severity: Medium
Advisory: GHSA-9236-8w7q-rmrv
CVE: CVE-2021-4162
CWE: CWE-352
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-9236-8w7q-rmrv
Type: github-advisory

## Affected
- PyPI: `archivy` — affected >=0 <1.6.2

## Details
archivy is vulnerable to Cross-Site Request Forgery (CSRF). There is [a fix](https://github.com/archivy/archivy/commit/796c3ae318eea183fc88c87ec5a27355b0f6a99d) available in the master branch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4162
- https://github.com/archivy/archivy/commit/796c3ae318eea183fc88c87ec5a27355b0f6a99d
- https://github.com/advisories/GHSA-9236-8w7q-rmrv
- https://github.com/archivy/archivy
- https://github.com/archivy/archivy/releases/tag/v1.6.2
- https://github.com/pypa/advisory-database/tree/main/vulns/archivy/PYSEC-2021-869.yaml
- https://huntr.dev/bounties/e204a768-2129-4b6f-abad-e436309c7c32
