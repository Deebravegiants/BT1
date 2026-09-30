# [C] Dokploy Broken Access Control on docker-container-terminal WebSocket (Member -> Root in Arbitrary Containers)

## Summary
Severity: Critical
Advisory: CVE-2026-72864
Aliases: GHSA-899j-cjwp-v4gw
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72864
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the local branch of /docker-container-terminal in apps/dokploy/server/wss/docker-container-terminal.ts authenticates with validateRequest but does not authorize the attacker-controlled containerId against the caller's role, organization, or service access before passing it to `docker exec`, allowing any authenticated member to obtain a root shell in arbitrary containers on a self-hosted instance. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72864.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-899j-cjwp-v4gw
- https://nvd.nist.gov/vuln/detail/CVE-2026-72864
- https://github.com/Dokploy/dokploy/commit/68f5afae42fca353dcb3d3bc6219ffe9e168cb91
