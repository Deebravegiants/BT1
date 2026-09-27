# [C] File Browser before 2.63.20 Privilege Escalation via Proxy Authentication

## Summary
Severity: Critical
Advisory: CVE-2026-72837
Aliases: GHSA-j7jh-37pf-mf8h
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-72837
Type: osv

## Details
File Browser versions before 2.63.20 fail to honor the createUserDir isolation in proxy and hook authentication auto-provisioning paths. Attackers with valid upstream-authenticated credentials can read, modify, delete, and share files belonging to other users by exploiting the server root scope assignment.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72837.json
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-j7jh-37pf-mf8h
- https://nvd.nist.gov/vuln/detail/CVE-2026-72837
- https://www.vulncheck.com/advisories/file-browser-before-privilege-escalation-via-proxy-authentication
