# [C] Craft CMS before 5.10.11 Authentication Bypass via Admin Flag Inheritance

## Summary
Severity: Critical
Advisory: CVE-2026-84795
Aliases: GHSA-242m-9wq7-vhwq
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84795
Type: osv

## Details
Craft CMS before 5.10.11 fails to validate the admin flag during user registration, allowing it to persist from deactivated admin accounts. Attackers can register with a deactivated admin's email address to inherit administrator privileges when public registration and disabled email verification are configured.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84795.json
- https://github.com/craftcms/cms/security/advisories/GHSA-242m-9wq7-vhwq
- https://nvd.nist.gov/vuln/detail/CVE-2026-84795
- https://www.vulncheck.com/advisories/craft-cms-before-5.10.11-authentication-bypass-via-admin-flag-inheritance
