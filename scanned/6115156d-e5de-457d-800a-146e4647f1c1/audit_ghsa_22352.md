# [M] Concrete CMS Cross-site Scripting via Survey Blocks

## Summary
Severity: Medium
Advisory: GHSA-7388-7vq2-m4f4
CVE: CVE-2021-28145
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7388-7vq2-m4f4
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <8.5.5

## Details
Concrete CMS (formerly concrete5) before 8.5.5 allows remote authenticated users to conduct Cross-site Scripting (XSS) attacks via a crafted survey block. This requires at least Editor privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28145
- https://documentation.concrete5.org/developers/introduction/version-history/855-release-notes
- https://github.com/S1lkys/CVE-2021-40101
- https://www.concrete5.org/developers/security
