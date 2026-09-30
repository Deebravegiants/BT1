# [M] Scoold: Persistent Admin Takeover by Overwriting the admins Configuration Setting via Forged JWT (missing `jti` validation)

## Summary
Severity: Medium
Advisory: CVE-2026-42176
Aliases: GHSA-7qfx-c234-xg4g
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-42176
Type: osv

## Details
Scoold is a Q&A and a knowledge sharing platform for teams. Prior to version 1.67.0, Scoold allows the admins configuration value to be modified through /api/config/set/admins with a forged Bearer token that is accepted as an admin API token. Once that setting is changed, the target email address is written to the application configuration file. The change does not become active immediately in the current process, because the ADMINS set is loaded once at startup. After a Scoold restart, though, the selected user is recognized as an administrator and gains access to the admin panel. This issue gives an attacker a reliable persistence path: write their own email into scoold.admins, wait for a restart or trigger one operationally, and the account comes back as admin. This issue has been patched in version 1.67.0.

## References
- https://github.com/Erudika/scoold/releases/tag/1.67.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42176.json
- https://github.com/Erudika/scoold/security/advisories/GHSA-7qfx-c234-xg4g
- https://nvd.nist.gov/vuln/detail/CVE-2026-42176
