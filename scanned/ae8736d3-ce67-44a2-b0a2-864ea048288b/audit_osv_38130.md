# [M] Combodo iTop: Improper access control in ajax.render.php and ajax.document.php

## Summary
Severity: Medium
Advisory: CVE-2026-34836
Aliases: GHSA-2gvp-4cv3-cx6j
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-34836
Type: osv

## Details
Combodo iTop is a web based IT service management tool. Prior to 3.2.3, improper access control in ajax.render.php and ajax.document.php allows for document access without checking on user permissions. This issue has been fixed in version 3.2.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34836.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-2gvp-4cv3-cx6j
- https://nvd.nist.gov/vuln/detail/CVE-2026-34836
- https://github.com/Combodo/iTop/commit/77915853875710f152a873842fa2a84ebd09719b
