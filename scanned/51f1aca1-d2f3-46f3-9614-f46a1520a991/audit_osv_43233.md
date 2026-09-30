# [H] Dokploy: Remote Code Execution (RCE) via Command Injection in settings.readTraefikFile

## Summary
Severity: High
Advisory: CVE-2026-72875
Aliases: GHSA-j3pv-r5wg-235m
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72875
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, settings.readTraefikFile in apps/dokploy/server/api/routers/settings.ts passes a path accepted by apiReadTraefikConfig to readConfigInPath in packages/server/src/utils/traefik/application.ts, where configPath is interpolated into execAsyncRemote as cat ${configPath}, allowing a user with traefikFiles.read permission to execute arbitrary commands on a managed server through shell metacharacters. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72875.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-j3pv-r5wg-235m
- https://nvd.nist.gov/vuln/detail/CVE-2026-72875
- https://github.com/Dokploy/dokploy/commit/92310ddb143c8e67ca95eb7db661838a76579f2e
- https://github.com/Dokploy/dokploy/pull/4873
