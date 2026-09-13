# [M] n8n: Regular Expression Denial of Service in the Default Blocked-File-Pattern Match via a Git Node Clone Path

## Summary
Severity: Medium
Advisory: CVE-2026-86081
Aliases: GHSA-j535-v25q-vx3q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-86081
Type: osv

## Details
n8n is an open source workflow automation platform. Prior to 1.123.76, 2.37.7, and 2.38.2, the Git node clone operation matched an attacker-controlled destination path against the default N8N_BLOCK_FILE_PATTERNS regular expression. The pattern ^(./).git(/.)$ allowed catastrophic backtracking and ran synchronously in the main n8n process. An authenticated workflow editor could therefore freeze the instance with one workflow execution; the affected default is declared in packages/@n8n/config/src/configs/security.config.ts. This issue is fixed in versions 1.123.76, 2.37.7 and 2.38.2.

## References
- https://github.com/n8n-io/n8n/releases/tag/n8n@1.123.76
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.37.7
- https://github.com/n8n-io/n8n/releases/tag/n8n@2.38.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86081.json
- https://github.com/n8n-io/n8n/security/advisories/GHSA-j535-v25q-vx3q
- https://nvd.nist.gov/vuln/detail/CVE-2026-86081
