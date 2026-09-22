# [C] Dokploy: Authenticated RCE via Command Injection in registry.testRegistry / registry.testRegistryById

## Summary
Severity: Critical
Advisory: CVE-2026-72902
Aliases: GHSA-w6r4-f26v-8g36
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72902
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, Dokploy allows an authenticated user to execute arbitrary commands on a local or SSH-connected target server because registry.testRegistry and registry.testRegistryById in apps/dokploy/server/api/routers/registry.ts interpolate the password field into an execAsyncRemote shell command instead of using safeDockerLoginCommand. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72902.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-w6r4-f26v-8g36
- https://nvd.nist.gov/vuln/detail/CVE-2026-72902
- https://github.com/Dokploy/dokploy/commit/d3f522b7a6f5100fc0fc0bff5851e48d11d459e2
- https://github.com/Dokploy/dokploy/pull/4875
