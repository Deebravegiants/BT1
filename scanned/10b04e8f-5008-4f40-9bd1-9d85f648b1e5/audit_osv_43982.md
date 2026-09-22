# [M] n8n before 2.34.1 Authorization Bypass via Custom Role Deletion

## Summary
Severity: Medium
Advisory: CVE-2026-77079
Aliases: GHSA-xhmh-8fgr-xqhj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:L/SC:H/SI:H/SA:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-77079
Type: osv

## Details
n8n before 2.34.1 and 2.33.4 contains an authorization bypass in the custom project role deletion (reassignment) path. When deleting a custom project role with a reassignment target, the code validated only that the target role existed and was project-scoped, performing no project-level authorization check. A user holding only the narrow role:manageProject global scope could delete any custom project role in use on the instance and reassign its holders (including themselves) to the built-in project:admin role, gaining full administrative control of projects they had no legitimate access to.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77079.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-xhmh-8fgr-xqhj
- https://nvd.nist.gov/vuln/detail/CVE-2026-77079
- https://www.vulncheck.com/advisories/n8n-before-authorization-bypass-via-custom-role-deletion
