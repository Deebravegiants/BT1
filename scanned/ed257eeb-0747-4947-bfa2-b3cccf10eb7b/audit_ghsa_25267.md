# [M] Dolibarr Stored Cross-site Scripting in expensereport/card.php

## Summary
Severity: Medium
Advisory: GHSA-r3r5-fqfm-9wrh
CVE: CVE-2018-16808
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r3r5-fqfm-9wrh
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=0 <7.0.1

## Details
An issue was discovered in Dolibarr through 7.0.0. There is Stored XSS in expensereport/card.php in the expense reports plugin via the comments parameter, or a public or private note.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16808
- https://github.com/Dolibarr/dolibarr/issues/9449
- https://github.com/Dolibarr/dolibarr
