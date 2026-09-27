# [M] OpenProject is Vulnerable to Insecure Direct Object Reference in Meetings

## Summary
Severity: Medium
Advisory: CVE-2026-22605
Aliases: GHSA-fq4m-pxvm-8x2j
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-22605
Type: osv

## Details
OpenProject is an open-source, web-based project management software. OpenProject versions prior to version 16.6.3, allowed users with the View Meetings permission on any project, to access meeting details of meetings that belonged to projects, the user does not have access to. This issue has been patched in version 16.6.3.

## References
- https://github.com/opf/openproject/releases/tag/v16.6.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22605.json
- https://github.com/opf/openproject/security/advisories/GHSA-fq4m-pxvm-8x2j
- https://nvd.nist.gov/vuln/detail/CVE-2026-22605
