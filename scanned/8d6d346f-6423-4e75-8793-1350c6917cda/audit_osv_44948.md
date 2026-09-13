# [C] Anchor CMS through 0.12.7 Privilege Escalation via Missing Authorization on Admin User-Management Endpoints

## Summary
Severity: Critical
Advisory: CVE-2026-88959
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88959
Type: osv

## Details
Anchor CMS through 0.12.7 fails to enforce role-based access control in admin user-management endpoints, allowing any authenticated low-privilege user to create administrator accounts or modify existing ones. Attackers with editor or user roles can POST directly to admin/users/add or admin/users/edit endpoints to create new administrator accounts or change the existing administrator's password, gaining full administrative access.

## References
- https://packagist.org
- https://gist.github.com/bozorovab2009-spec/57931237f774b78333f8fe47e84ec4aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88959.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-88959
- https://www.vulncheck.com/advisories/anchor-cms-through-0.12.7-privilege-escalation-via-missing-authorization-on-admin-user-management-endpoints
- https://github.com/anchorcms/anchor-cms
- https://github.com/anchorcms/anchor-cms/blob/0.12.7/anchor/routes/users.php
