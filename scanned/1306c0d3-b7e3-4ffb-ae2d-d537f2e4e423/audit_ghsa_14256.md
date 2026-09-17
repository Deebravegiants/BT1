# [H] Uvdesk remote code execution vulnerability

## Summary
Severity: High
Advisory: GHSA-2hw6-4rv9-82fp
CVE: CVE-2023-0265
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-05
Source: https://github.com/advisories/GHSA-2hw6-4rv9-82fp
Type: github-advisory

## Affected
- Packagist: `uvdesk/community-skeleton` — affected >=0

## Details
Uvdesk version 1.1.1 allows an authenticated remote attacker to execute commands on the server. This is possible because the application does not properly validate profile pictures uploaded by customers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0265
- https://fluidattacks.com/advisories/supply
- https://github.com/uvdesk/community-skeleton
