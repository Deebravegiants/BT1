# [M] Canvs Canvas Cross-site Scripting (XSS) via title and content fields

## Summary
Severity: Medium
Advisory: GHSA-3657-q433-mmpx
CVE: CVE-2017-8298
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-3657-q433-mmpx
Type: github-advisory

## Affected
- Packagist: `austintoddj/canvas` — affected 3.3.0

## Details
cnvs.io Canvas 3.3.0 has XSS in the title and content fields of a "Posts > Add New" action, and during creation of new tags and users.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-8298
- https://github.com/cnvs/canvas/issues/331
- https://github.com/austintoddj/canvas
