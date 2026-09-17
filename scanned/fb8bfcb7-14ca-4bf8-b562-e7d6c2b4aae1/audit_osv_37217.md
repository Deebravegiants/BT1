# [C] Vito: Cross-project privilege escalation in workflow site-creation actions allows unauthorized server modification

## Summary
Severity: Critical
Advisory: CVE-2026-29789
Aliases: GHSA-3m6w-8qh4-qr76
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-29789
Type: osv

## Details
Vito is a self-hosted web application that helps manage servers and deploy PHP applications into production servers. Prior to version 3.20.3, a missing authorization check in workflow site-creation actions allows an authenticated attacker with workflow write access in one project to create/manage sites on servers belonging to other projects by supplying a foreign server_id. This issue has been patched in version 3.20.3.

## References
- https://github.com/vitodeploy/vito/releases/tag/3.20.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29789.json
- https://github.com/vitodeploy/vito/security/advisories/GHSA-3m6w-8qh4-qr76
- https://nvd.nist.gov/vuln/detail/CVE-2026-29789
- https://github.com/vitodeploy/vito/commit/0fdcfe5f0b93da644a0456e0e4544763828e3326
- https://github.com/vitodeploy/vito/pull/1036
