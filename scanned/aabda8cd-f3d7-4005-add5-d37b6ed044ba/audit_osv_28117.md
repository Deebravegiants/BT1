# [M] Sensitive fields access through dropdowns in GLPI

## Summary
Severity: Medium
Advisory: CVE-2024-27930
Aliases: GHSA-82vv-j9pr-qmwq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-27930
Type: osv

## Details
GLPI is a Free Asset and IT Management Software package, Data center management, ITIL Service Desk, licenses tracking and software auditing. An authenticated user can access sensitive fields data from items on which he has read access. This issue has been patched in version 10.0.13.

## References
- https://borelenzo.github.io/stuff/2024/02/29/glpi-pwned.html
- https://github.com/glpi-project/glpi/releases/tag/10.0.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27930.json
- https://github.com/glpi-project/glpi/security/advisories/GHSA-82vv-j9pr-qmwq
- https://nvd.nist.gov/vuln/detail/CVE-2024-27930
- https://github.com/glpi-project/glpi/commit/1942b70b2422fff51822f6eb3af500c94760871e
