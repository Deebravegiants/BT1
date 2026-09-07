# [M] Authenticated path traversal in Umbraco CMS

## Summary
Severity: Medium
Advisory: GHSA-936x-wgqv-hhgq
CVE: CVE-2020-5811
CWE: CWE-22
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-936x-wgqv-hhgq
Type: github-advisory

## Affected
- NuGet: `UmbracoCms` — affected >=0 <8.9.2

## Details
An authenticated path traversal vulnerability exists during package installation in Umbraco CMS <= 8.9.1 or current, which could result in arbitrary files being written outside of the site home and expected paths when installing an Umbraco package.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5811
- https://www.tenable.com/security/research/tra-2020-59
- http://packetstormsecurity.com/files/163965/Umbraco-CMS-8.9.1-Traversal-Arbitrary-File-Write.html
