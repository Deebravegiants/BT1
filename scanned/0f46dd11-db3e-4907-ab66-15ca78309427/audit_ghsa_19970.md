# [M] Snipe-IT allows attackers to check whether a user account exists

## Summary
Severity: Medium
Advisory: GHSA-qqv9-gqh5-7h99
CVE: CVE-2022-44381
CWE: CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-12-25
Source: https://github.com/advisories/GHSA-qqv9-gqh5-7h99
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0

## Details
Snipe-IT through 6.0.14 allows attackers to check whether a user account exists because of response variations in a /password/reset request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-44381
- https://census-labs.com/news/2022/12/23/multiple-vulnerabilities-in-snipe-it
- https://github.com/snipe/snipe-it
