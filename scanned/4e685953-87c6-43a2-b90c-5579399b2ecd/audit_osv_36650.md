# [C] Dokploy Vulnerable to Authenticated Remote Code Execution via Command Injection in Docker Container Terminal WebSocket Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-24841
Aliases: GHSA-vx6x-6559-x35r
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-24841
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In versions prior to 0.26.6, a critical command injection vulnerability exists in Dokploy's WebSocket endpoint `/docker-container-terminal`. The `containerId` and `activeWay` parameters are directly interpolated into shell commands without sanitization, allowing authenticated attackers to execute arbitrary commands on the host server. Version 0.26.6 fixes the issue.

## References
- https://github.com/Dokploy/dokploy/blob/canary/apps/dokploy/server/wss/docker-container-terminal.ts
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24841.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-vx6x-6559-x35r
- https://nvd.nist.gov/vuln/detail/CVE-2026-24841
- https://github.com/Dokploy/dokploy/commit/74e0bd5fe3ef7199f44fcd19c6f5a2f09b806d6f
