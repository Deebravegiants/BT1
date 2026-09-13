# [C] Dokploy: Command Injection via Registry Credentials in Swarm Upload

## Summary
Severity: Critical
Advisory: CVE-2026-72879
Aliases: GHSA-prwq-2mcm-mvhr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72879
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.8, the getRegistryCommands() function in packages/server/src/utils/cluster/upload.ts interpolates registry.password and registry.registryUrl directly into a shell command without escaping. An authenticated user with project access can configure malicious registry credentials and trigger a swarm deployment to execute arbitrary OS commands on the Dokploy server, read or modify host files, and access other containers through Docker. This issue is fixed in version 0.29.8.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72879.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-prwq-2mcm-mvhr
- https://nvd.nist.gov/vuln/detail/CVE-2026-72879
- https://github.com/Dokploy/dokploy/commit/1f4f94042f1d874349c42d8ae7fee51346cd086e
- https://github.com/Dokploy/dokploy/pull/4579
