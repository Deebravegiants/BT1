# [H] SuiteCRM's Inconsistent RBAC Enforcement Enables Access Control Bypass

## Summary
Severity: High
Advisory: CVE-2025-64490
Aliases: GHSA-jh8v-wqgj-hhc2
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)
Published: 2025-11-08
Source: https://osv.dev/vulnerability/CVE-2025-64490
Type: osv

## Details
SuiteCRM is an open-source, enterprise-ready Customer Relationship Management (CRM) software application. Versions 7.14.7 and prior, 8.0.0-beta.1 through 8.9.0 allow a low-privileged user with a restrictive role to view and create work items through the Resource Calendar and project screens, even when the related modules (Projects, Project Tasks, Tasks, Leads, Accounts, Meetings, Calls) are explicitly set to Disabled/None in Role Management. This indicates inconsistent ACL/RBAC enforcement across modules and views, resulting in unauthorized data exposure and modification. This issue is fixed in versions 7.14.8 and 8.9.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64490.json
- https://github.com/SuiteCRM/SuiteCRM/security/advisories/GHSA-jh8v-wqgj-hhc2
- https://nvd.nist.gov/vuln/detail/CVE-2025-64490
