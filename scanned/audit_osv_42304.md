# [H] Apache CloudStack: ProjectRole & ProjectRolePermission authorization issue

## Summary
Severity: High
Advisory: CVE-2026-66722
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-66722
Type: osv

## Details
Improper authorization for CRUD operations on Project Roles and Project Role permissions for domain admins in CloudStack.




A Domain Admin can create, update, delete, and list project roles and project role permissions for projects in any domain, not just their own. The check only confirms the caller is a Domain Admin, without verifying whether the target project belongs to their domain or subdomain. This allows a malicious Domain Admin to tamper with project roles and permissions across unrelated domains.




This issue affects Apache CloudStack: from 4.15.0.0 through 4.20.3.0 and from 4.21.0.0 through 4.22.1.0.





Users are recommended to upgrade to version 4.20.3.1 or 4.22.1.1 or later, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66722.json
- https://lists.apache.org/thread/g6cwddtjrwbh1d56wjz4cfp3fzfm4kbc
- https://nvd.nist.gov/vuln/detail/CVE-2026-66722
