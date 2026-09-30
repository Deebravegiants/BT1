# [C] Dokploy: OS Command Injection in backup/restore pipeline via unescaped user-controlled shell arguments

## Summary
Severity: Critical
Advisory: CVE-2026-72878
Aliases: GHSA-p2c7-8j28-c7gq
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72878
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). Prior to 0.29.13, Dokploy's backup and restore pipeline constructs shell commands by directly interpolating user-controlled database fields into bash -c "..." and sh -c "..." strings, then executes them via child_process.exec(). An authenticated admin/owner can inject arbitrary OS commands that execute on the host machine running Dokploy (not just inside a container). This vulnerability is fixed in 0.29.13.

## References
- https://github.com/Dokploy/dokploy/releases/tag/v0.29.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72878.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-p2c7-8j28-c7gq
- https://nvd.nist.gov/vuln/detail/CVE-2026-72878
- https://github.com/Dokploy/dokploy/commit/d02f34f9d48b363b9bf15a948e263ff4ebfcceda
- https://github.com/Dokploy/dokploy/pull/4873
