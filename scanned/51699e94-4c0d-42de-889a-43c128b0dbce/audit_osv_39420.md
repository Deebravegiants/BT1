# [C] Dokploy: Remote Code Execution through Path Traversal

## Summary
Severity: Critical
Advisory: CVE-2026-45661
Aliases: GHSA-66v7-g3fh-47h3
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-45661
Type: osv

## Details
Dokploy is a free, self-hostable Platform as a Service (PaaS). In 0.26.5 and earlier, a critical path traversal vulnerability exists in Dokploy v0.26.5 that allows authenticated users to write arbitrary files to the filesystem during application deployment. When combined with Dokploy's remote server deployment feature, this vulnerability enables arbitrary file write to remote server filesystems, automatic remote code execution via cron jobs, complete server compromise, data exfiltration without user interaction, and persistent backdoor installation. This vulnerability bypasses all container isolation on remote server deployments.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45661.json
- https://github.com/Dokploy/dokploy/security/advisories/GHSA-66v7-g3fh-47h3
- https://nvd.nist.gov/vuln/detail/CVE-2026-45661
