# [C] phpMyFAQ - Privilege Escalation via Missing SuperAdmin Guard in user/add Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-57996
Aliases: GHSA-r2f4-v277-hvw9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-57996
Type: osv

## Details
phpMyFAQ before 4.1.5 contains a privilege escalation vulnerability in the user/add API endpoint that allows non-SuperAdmin administrators to create SuperAdmin accounts. A delegated administrator with USER_ADD/EDIT/DELETE permissions can call POST /admin/api/user/add with isSuperAdmin: true and attacker-chosen credentials to create a SuperAdmin account, then authenticate as that account to achieve full instance takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57996.json
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-r2f4-v277-hvw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-57996
- https://www.vulncheck.com/advisories/phpmyfaq-privilege-escalation-via-missing-superadmin-guard-in-user-add-endpoint
