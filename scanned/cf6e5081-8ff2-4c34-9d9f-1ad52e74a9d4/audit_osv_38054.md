# [C] Vvveb < 1.0.8.1 Privilege Escalation via admin/user/save

## Summary
Severity: Critical
Advisory: CVE-2026-34427
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-34427
Type: osv

## Details
Vvveb prior to 1.0.8.1 contains a privilege escalation vulnerability in the admin user profile save endpoint that allows authenticated users to modify privileged fields on their own profile. Attackers can inject role_id=1 into profile save requests to escalate to Super Administrator privileges, enabling plugin upload functionality for remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34427.json
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.1
- https://nvd.nist.gov/vuln/detail/CVE-2026-34427
- https://www.vulncheck.com/advisories/vvveb-privilege-escalation-via-admin-user-save
- https://github.com/givanz/Vvveb/commit/0eca14af50f038915b8bf7ceec2becf6b6720b0a
- https://github.com/givanz/Vvveb
