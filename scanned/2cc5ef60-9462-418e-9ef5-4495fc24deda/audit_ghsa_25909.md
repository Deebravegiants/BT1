# [H] XSS in doc_link

## Summary
Severity: High
Advisory: GHSA-2v82-5746-vwqc
CVE: CVE-2021-29625
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-2v82-5746-vwqc
Type: github-advisory

## Affected
- Packagist: `vrana/adminer` — affected >=4.7.8 <4.8.1

## Details
### Impact
Users of MySQL, MariaDB, PgSQL and SQLite are affected. XSS is in most cases prevented by strict CSP in all modern browsers. The only exception is when Adminer is using a `pdo_` extension to communicate with the database (it is used if the native extensions are not enabled). In browsers without CSP, Adminer versions 4.6.1 to 4.8.0 are affected.

### Patches
Patched by 4043092, included in version [4.8.1](https://github.com/vrana/adminer/releases/tag/v4.8.1).

### Workarounds
Do both:
* Use browser supporting strict CSP.
* Enable the native PHP extensions (e.g. `mysqli`) or disable displaying PHP errors (`display_errors`).

### References
https://sourceforge.net/p/adminer/bugs-and-features/797/

### For more information
If you have any questions or comments about this advisory:
* Comment at 4043092.

## References
- https://github.com/vrana/adminer/security/advisories/GHSA-2v82-5746-vwqc
- https://nvd.nist.gov/vuln/detail/CVE-2021-29625
- https://github.com/vrana/adminer/commit/4043092ec2c0de2258d60a99d0c5958637d051a7
- https://packagist.org/packages/vrana/adminer
- https://sourceforge.net/p/adminer/bugs-and-features/797
