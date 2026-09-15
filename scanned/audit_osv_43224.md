# [C] Dokploy: OS Command Injection via compose `composePath`

## Summary
Severity: Critical
Advisory: CVE-2026-72865
Aliases: GHSA-8r5w-vqjr-8c44
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72865
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the compose.update operation stores an unvalidated composePath that packages/server/src/utils/builders/compose.ts and packages/server/src/services/compose.ts interpolate into docker compose -f, docker stack deploy -c, and touch shell commands executed through /bin/sh -c. An authenticated member with compose write and deploy permission can supply a crafted composePath, trigger compose.deploy or startCompose, and execute arbitrary operating-system commands in the Docker-privileged Dokploy host context. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72865.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-8r5w-vqjr-8c44
- https://nvd.nist.gov/vuln/detail/CVE-2026-72865
- https://github.com/Dokploy/dokploy/commit/d48037a80203bb0ecaec4f5653aef75fcfdb656d
- https://github.com/Dokploy/dokploy/pull/4863
