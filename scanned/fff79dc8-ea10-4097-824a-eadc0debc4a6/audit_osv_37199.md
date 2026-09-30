# [H] SuiteCRM has a REST API V8 IDOR: Missing ACL Checks on User Preferences and Relationship Endpoints

## Summary
Severity: High
Advisory: CVE-2026-29189
Aliases: GHSA-m6x8-3hxp-qxwv
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-19
Source: https://osv.dev/vulnerability/CVE-2026-29189
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Prior to versions 7.15.1 and 8.9.3, the SuiteCRM REST API V8 has missing ACL (Access Control List) checks on several endpoints, allowing authenticated users to access and manipulate data they should not have permission to interact with. Versions 7.15.1 and 8.9.3 patch the issue.

## References
- https://docs.suitecrm.com/admin/releases/7.15.x
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29189.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-m6x8-3hxp-qxwv
- https://nvd.nist.gov/vuln/detail/CVE-2026-29189
