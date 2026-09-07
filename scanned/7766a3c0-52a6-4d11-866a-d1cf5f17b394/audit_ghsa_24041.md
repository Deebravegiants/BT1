# [M] MantisBT XSS via move_attachments_page.php

## Summary
Severity: Medium
Advisory: GHSA-x53v-v9xp-gf6g
CVE: CVE-2017-7241
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-x53v-v9xp-gf6g
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <1.3.9
- Packagist: `mantisbt/mantisbt` — affected >=2.0.0 <2.1.3
- Packagist: `mantisbt/mantisbt` — affected >=2.2.0 <2.2.3

## Details
A cross-site scripting (XSS) vulnerability in the MantisBT Move Attachments page (move_attachments_page.php, part of admin tools) allows remote attackers to inject arbitrary code through a crafted 'type' parameter, if Content Security Protection (CSP) settings allows it. This is fixed in 1.3.9, 2.1.3, and 2.2.3. Note that this vulnerability is not exploitable if the admin tools directory is removed, as recommended in the "Post-installation and upgrade tasks" of the MantisBT Admin Guide. A reminder to do so is also displayed on the login page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7241
- https://github.com/mantisbt/mantisbt/commit/2d55c6476e939db021128b3995c28dcae05b09a4
- https://github.com/mantisbt/mantisbt/commit/d31841c806a3c8379fcf6c9d9559451270b0f1cb
- https://github.com/mantisbt/mantisbt/commit/ecef0e9b523a460709e8feedfce72f05bb30b992
- https://github.com/mantisbt/mantisbt
- http://www.mantisbt.org/bugs/view.php?id=22568
