# [H] SQL Injection in t3/dce

## Summary
Severity: High
Advisory: GHSA-5v5h-4w2g-gxxc
CVE: CVE-2021-31777
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-06-08
Source: https://github.com/advisories/GHSA-5v5h-4w2g-gxxc
Type: github-advisory

## Affected
- Packagist: `t3/dce` — affected >=2.2.0 <2.6.2

## Details
The dce (aka Dynamic Content Element) extension 2.2.0 through 2.6.x before 2.6.2, and 2.7.x before 2.7.1, for TYPO3 allows SQL Injection via a backend user account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31777
- https://bitbucket.org/ArminVieweg/dce/commits/998a2392f69f2153797c5ace6e8914ca309e70c7
- https://excellium-services.com/cert-xlm-advisory
- https://packagist.org/packages/t3/dce
- https://typo3.org/security/advisory/typo3-ext-sa-2021-005
- http://packetstormsecurity.com/files/162429/TYPO3-6.2.1-SQL-Injection.html
