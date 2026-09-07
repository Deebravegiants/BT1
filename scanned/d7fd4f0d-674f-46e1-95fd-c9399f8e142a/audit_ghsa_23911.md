# [M] MantisBT XSS via adm_config_report.php's action parameter

## Summary
Severity: Medium
Advisory: GHSA-v7qf-22rw-chph
CVE: CVE-2017-6973
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v7qf-22rw-chph
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <1.3.8
- Packagist: `mantisbt/mantisbt` — affected >=2.0.0 <2.1.2
- Packagist: `mantisbt/mantisbt` — affected >=2.2.0 <2.2.2

## Details
A cross-site scripting (XSS) vulnerability in the MantisBT Configuration Report page (adm_config_report.php) allows remote attackers to inject arbitrary code through a crafted 'action' parameter. This is fixed in 1.3.8, 2.1.2, and 2.2.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6973
- https://github.com/mantisbt/mantisbt/commit/034cd07b47af37366fc7b726cb4a4f971d3d3fb9
- https://github.com/mantisbt/mantisbt/commit/15e52e84c389afe8b03ed3cdb59b6549257ed197
- https://github.com/mantisbt/mantisbt/commit/da74c5aa02bcf21cfaab1180f892c22415e5fea6
- https://github.com/mantisbt/mantisbt
- http://www.mantisbt.org/bugs/view.php?id=22537
