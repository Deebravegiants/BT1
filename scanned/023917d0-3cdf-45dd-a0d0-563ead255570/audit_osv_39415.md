# [C] Dokploy: Command Injection via Unescaped Branch Fields in Deployment Pipeline

## Summary
Severity: Critical
Advisory: CVE-2026-45628
Aliases: GHSA-3frc-cfh9-ch2c
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45628
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In 0.29.2 and earlier, Dokploy constructs shell commands using JavaScript template literals and executes them via child_process.exec() (which runs through /bin/sh -c). User-supplied branch names, repository URLs, and Docker credentials are interpolated directly into these commands without escaping. This requires an authenticated user with application create/edit privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45628.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-3frc-cfh9-ch2c
- https://nvd.nist.gov/vuln/detail/CVE-2026-45628
