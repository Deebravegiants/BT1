# [M] Dokploy: Command Injection via Compose Shell Execution

## Summary
Severity: Medium
Advisory: CVE-2026-72739
Aliases: GHSA-5xv2-7f8w-9j5c
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72739
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, the createCommand() function constructs shell commands by interpolating compose service names and configuration into bash command strings. When a compose with a maliciously crafted name or service definition is deployed, the shell metacharacters are interpreted as command separators, allowing arbitrary command execution on the Docker host. This vulnerability is fixed in 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72739.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-5xv2-7f8w-9j5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-72739
- https://github.com/Dokploy/dokploy/commit/d48037a80203bb0ecaec4f5653aef75fcfdb656d
