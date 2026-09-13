# [C] Grav Admin Plugin — IDOR Privilege Escalation via saveUser()

## Summary
Severity: Critical
Advisory: CVE-2026-59190
Aliases: GHSA-p97c-g455-q447
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-59190
Type: osv

## Details
grav-plugin-admin is an HTML user interface that provides a way to configure Grav and create and modify pages. In 1.10.52 and earlier, an authenticated attacker with admin.users permission can change the password of any user account, including the super administrator, by sending a direct POST request to /admin/user/{username}?task=save with data[password] because saveUser authorizes the caller's user-management permission but does not verify whether the caller may edit the target user. This issue is expected to be fixed in version 1.10.53.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59190.json
- https://github.com/getgrav/grav/security/advisories/GHSA-p97c-g455-q447
- https://nvd.nist.gov/vuln/detail/CVE-2026-59190
- https://github.com/getgrav/grav-plugin-admin/commit/88f7ce8e50324472f492965caa42fb709a4f791a
