# [M] MantisBT vulnerable to XSS due to improper escape in manage_plugin_page.php and manage_plugin_uninstall.php

## Summary
Severity: Medium
Advisory: GHSA-rqgj-rqfr-5j6f
CVE: CVE-2022-26144
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-14
Source: https://github.com/advisories/GHSA-rqgj-rqfr-5j6f
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.25.3

## Details
An XSS issue was discovered in MantisBT before 2.25.3. Improper escaping of a Plugin name allows execution of arbitrary code (if CSP allows it) in manage_plugin_page.php and manage_plugin_uninstall.php when a crafted plugin is installed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26144
- https://github.com/mantisbt/mantisbt/commit/a7751c3e318011ca1314bc1cfea200d53e0dfff6
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=29688
