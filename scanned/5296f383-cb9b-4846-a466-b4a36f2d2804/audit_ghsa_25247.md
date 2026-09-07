# [M] MantisBT XSS allows unsanitized input via admin/install.php

## Summary
Severity: Medium
Advisory: GHSA-98xr-mmq5-vc5h
CVE: CVE-2017-12061
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-98xr-mmq5-vc5h
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <1.3.12
- Packagist: `mantisbt/mantisbt` — affected >=2.0.0 <2.5.2

## Details
An XSS issue was discovered in admin/install.php in MantisBT before 1.3.12 and 2.x before 2.5.2. Some variables under user control in the MantisBT installation script are not properly sanitized before being output, allowing remote attackers to inject arbitrary JavaScript code, as demonstrated by the $f_database, $f_db_username, and $f_admin_username variables. This is mitigated by the fact that the admin/ folder should be deleted after installation, and also prevented by CSP.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12061
- https://github.com/mantisbt/mantisbt/commit/17f9b94f031ba93ae2a727bca0e68458ecd08fb0
- https://github.com/mantisbt/mantisbt/commit/c73ae3d3d4dd4681489a9e697e8ade785e27cba5
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=23146
- https://web.archive.org/web/20170811053146/http://www.securitytracker.com/id/1039030
- http://openwall.com/lists/oss-security/2017/08/01/1
- http://openwall.com/lists/oss-security/2017/08/01/2
