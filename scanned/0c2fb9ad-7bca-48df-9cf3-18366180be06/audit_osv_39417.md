# [C] Dokploy: Authenticated Remote Code Execution via Command Injection in updateTraefikConfig Echo Statement

## Summary
Severity: Critical
Advisory: CVE-2026-45630
Aliases: GHSA-p787-6gqg-cvp5
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45630
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In 0.28.8 and earlier, authenticated OS command injection in the application.updateTraefikConfig tRPC endpoint allows admin/owner users to execute arbitrary system commands on remote servers via unsanitized echo shell interpolation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45630.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-p787-6gqg-cvp5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45630
