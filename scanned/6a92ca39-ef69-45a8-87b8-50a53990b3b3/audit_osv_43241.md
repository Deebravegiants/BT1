# [C] Dokploy: Command Injection via Compose Custom Command

## Summary
Severity: Critical
Advisory: CVE-2026-72884
Aliases: GHSA-qh6h-669j-77rw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72884
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, sanitizeCommand in packages/server/src/utils/builders/compose.ts only trims whitespace and strips surrounding quotes from compose.command before exportEnvCommand and docker command interpolation, allowing an authenticated user who can update a Compose service to inject shell metacharacters and execute arbitrary commands on the Dokploy host. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72884.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-qh6h-669j-77rw
- https://nvd.nist.gov/vuln/detail/CVE-2026-72884
- https://github.com/Dokploy/dokploy/commit/d48037a80203bb0ecaec4f5653aef75fcfdb656d
- https://github.com/Dokploy/dokploy/pull/4863
