# [M] MantisBT vulnerable to XSS through config_option parameter in adm_config_report.php

## Summary
Severity: Medium
Advisory: GHSA-4w6c-3hcx-rfj5
CVE: CVE-2017-7309
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4w6c-3hcx-rfj5
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <1.3.9
- Packagist: `mantisbt/mantisbt` — affected >=2.1.0 <2.1.3
- Packagist: `mantisbt/mantisbt` — affected >=2.2.0 <2.2.3

## Details
A cross-site scripting (XSS) vulnerability in the MantisBT Configuration Report page (adm_config_report.php) allows remote attackers to inject arbitrary code (if CSP settings permit it) through a crafted 'config_option' parameter. This is fixed in 1.3.9, 2.1.3, and 2.2.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7309
- https://github.com/mantisbt/mantisbt/commit/0243375e32bc24878e309f3d6ef6d8cfb3e2f278
- https://github.com/mantisbt/mantisbt/commit/c9e5b1d0404503022605459552faeaf610bf15ae
- https://github.com/mantisbt/mantisbt/commit/e881dd79df422033bbea88914fc0a717fae40358
- https://github.com/mantisbt/mantisbt
- http://openwall.com/lists/oss-security/2017/03/30/4
- http://www.mantisbt.org/bugs/view.php?id=22579
