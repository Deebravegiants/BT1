# [H] Deskflow: Local privilege escalation via unauthenticated IPC

## Summary
Severity: High
Advisory: CVE-2026-41477
Aliases: GHSA-6rx5-g478-775c
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41477
Type: osv

## Details
Deskflow is a keyboard and mouse sharing app.  In 1.20.0, 1.26.0.134, and earlier, Deskflow daemon runs as SYSTEM and exposes an IPC named pipe with WorldAccessOption enabled. The daemon processes privileged commands without authentication, allowing any local unprivileged user to execute arbitrary commands as SYSTEM. Affects both stable v1.20.0 + and Continuous v1.26.0.134 prerelease.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41477.json
- https://github.com/deskflow/deskflow/security/advisories/GHSA-6rx5-g478-775c
- https://nvd.nist.gov/vuln/detail/CVE-2026-41477
