# [M] FOSSBilling's missing self-edit prevention in staff permission management allows persistent privilege escalation

## Summary
Severity: Medium
Advisory: CVE-2026-53645
Aliases: GHSA-4hf7-xxxw-64rm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:H/SI:H/SA:L)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-53645
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. Versions prior to 0.8.0 allow a low-privileged staff account to grant arbitrary module permissions to itself through the admin API, resulting in persistent privilege escalation. A staff user that only has `staff.create_and_edit_staff` can call `/api/admin/staff/permissions_update` targeting their own account and write any permission structure, bypassing the intended role-based access control boundary. Version 0.8.0 patches the issue. Some workarounds are available. Restrict the `staff.create_and_edit_staff` permission to only highly trusted staff members and/or use a reverse proxy or WAF to restrict access to `/api/admin/staff/permissions_update` to specific trusted roles.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53645.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-4hf7-xxxw-64rm
- https://nvd.nist.gov/vuln/detail/CVE-2026-53645
