# [M] Cross-site Scripting vulnerability in drag-and-drop upload of phpMyAdmin

## Summary
Severity: Medium
Advisory: GHSA-6hr3-44gx-g6wh
CVE: CVE-2023-25727
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-13
Source: https://github.com/advisories/GHSA-6hr3-44gx-g6wh
Type: github-advisory

## Affected
- Packagist: `phpmyadmin/phpmyadmin` — affected >=4.3.0 <4.9.11
- Packagist: `phpmyadmin/phpmyadmin` — affected >=5.0 <5.2.1

## Details
In phpMyAdmin before 4.9.11 and 5.x before 5.2.1, an authenticated user can trigger Cross-site Scripting (XSS) by uploading a crafted .sql file through the drag-and-drop interface. By disabling the configuration directive `$cfg['enable_drag_drop_import']`, users will be unable to use the drag and drop upload which would protect against the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-25727
- https://github.com/phpmyadmin/phpmyadmin/commit/53f70fd7f3b388639922e6cc1ca51fbe890c91cc
- https://github.com/phpmyadmin/phpmyadmin/commit/efa2406695551667f726497750d3db91fb6f662e
- https://github.com/phpmyadmin/composer
- https://www.phpmyadmin.net/security/PMASA-2023-1
