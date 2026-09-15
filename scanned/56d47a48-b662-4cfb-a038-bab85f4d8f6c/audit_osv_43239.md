# [C] Dokploy: Authenticated blind command injection via file mounts leads to direct remote host RCE on managed servers

## Summary
Severity: Critical
Advisory: CVE-2026-72882
Aliases: GHSA-qcf5-jjjp-7794
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72882
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In 0.28.8 and earlier, an authenticated user who can create or update file mounts for a service can inject shell metacharacters into filePath, causing Dokploy to execute attacker-controlled commands on the configured remote managed server over SSH. In the default deployment model, this yields direct remote host RCE from the web interface.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72882.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-qcf5-jjjp-7794
- https://nvd.nist.gov/vuln/detail/CVE-2026-72882
