# [H] WWBN AVideo has predictable default admin credentials in official Docker deployment path

## Summary
Severity: High
Advisory: CVE-2026-33037
Aliases: GHSA-89rv-p523-6wg9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33037
Type: osv

## Details
WWBN AVideo is an open source video platform. In versions 25.0 and below, the official Docker deployment files (docker-compose.yml, env.example) ship with the admin password set to "password", which is automatically used to seed the admin account during installation, meaning any instance deployed without overriding SYSTEM_ADMIN_PASSWORD is immediately vulnerable to trivial administrative takeover. No compensating controls exist: there is no forced password change on first login, no complexity validation, no default-password detection, and the password is hashed with weak MD5. Full admin access enables user data exposure, content manipulation, and potential remote code execution via file uploads and plugin management. The same insecure-default pattern extends to database credentials (avideo/avideo), compounding the risk. Exploitation depends on operators failing to change the default, a condition likely met in quick-start, demo, and automated deployments. This issue has been fixed in version 26.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33037.json
- https://github.com/WWBN/AVideo/security/advisories/GHSA-89rv-p523-6wg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33037
- https://github.com/WWBN/AVideo/commit/2075fac1a51f21fab5d8592235a095aa354a9de6
