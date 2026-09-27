# [C] Dokploy: OS Command Injection in registry credential testing and Swarm cluster management → HOST RCE

## Summary
Severity: Critical
Advisory: CVE-2026-72736
Aliases: GHSA-4mfc-grxw-6858
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72736
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, Dokploy passes user-controlled values directly into shell commands via unquoted template literal interpolation in the registry credential testing and Docker Swarm cluster management endbpoints. Both endpoints have a safe local code path (using execFileAsync or the Docker API) but a vulnerable remote path (using execAsyncRemote which runs the shell string via SSH). This vulnerability is fixed in 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72736.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-4mfc-grxw-6858
- https://nvd.nist.gov/vuln/detail/CVE-2026-72736
- https://github.com/Dokploy/dokploy/commit/df2779eaeb4a58f0c85d4caa713c776c790fa708
