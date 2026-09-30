# [M] MixPHP Framework has an SQL injection vulnerability via crafted `data` array

## Summary
Severity: Medium
Advisory: GHSA-q57j-rwwx-7rwp
CVE: CVE-2026-42474
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-01
Source: https://github.com/advisories/GHSA-q57j-rwwx-7rwp
Type: github-advisory

## Affected
- Packagist: `mix/mix` — affected >=2.0.0

## Details
SQL injection vulnerability in MixPHP Framework 2.x thru 2.2.17 via crafted `data` array to the data function in BuildHelper.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42474
- https://gist.github.com/sgInnora/fa46386840fe978a30d7e53c458f2975
- https://github.com/mix-php/mix
- https://github.com/mix-php/mix/blob/v2.2.17/src/database/src/Helper/BuildHelper.php
