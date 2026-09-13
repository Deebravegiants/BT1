# [C] Pagekit CMS has an Insecure Direct Object Reference (IDOR) in its User Role component

## Summary
Severity: Critical
Advisory: GHSA-w3j8-9p3j-3wjx
CVE: CVE-2025-67165
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-17
Source: https://github.com/advisories/GHSA-w3j8-9p3j-3wjx
Type: github-advisory

## Affected
- Packagist: `pagekit/pagekit` — affected >=0

## Details
An Insecure Direct Object Reference (IDOR) in Pagekit CMS v1.0.18 allows attackers to escalate privileges.

The project was archived as of December 1, 2023.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67165
- https://github.com/mbiesiad/vulnerability-research/tree/main/CVE-2025-67165
- https://github.com/pagekit/docs/blob/develop/user-interface/users.md#permissions
- https://github.com/pagekit/docs/blob/develop/user-interface/users.md#roles
- https://github.com/pagekit/pagekit
