# [C] Dokploy: Command Injection via Docker Credentials in buildRemoteDocker

## Summary
Severity: Critical
Advisory: CVE-2026-72870
Aliases: GHSA-g9cg-4mmj-mh7p
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72870
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the buildRemoteDocker() function in packages/server/src/utils/providers/docker.ts interpolates the application-controlled dockerImage value directly into a docker pull shell command. An authenticated user with project access can set a crafted dockerImage through application.update and trigger application.deploy, causing execAsync() to execute arbitrary operating-system commands as the Dokploy server process. This issue is fixed in version 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72870.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-g9cg-4mmj-mh7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-72870
- https://github.com/Dokploy/dokploy/commit/cba0b253c7de4157dd932de7f16a2ad247c7cee9
- https://github.com/Dokploy/dokploy/pull/4860
