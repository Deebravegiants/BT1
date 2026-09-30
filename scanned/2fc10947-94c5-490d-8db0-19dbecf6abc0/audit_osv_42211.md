# [M] SiYuan before v3.7.2 Path Traversal via /export/temp/

## Summary
Severity: Medium
Advisory: CVE-2026-65607
Aliases: GHSA-gw25-m53r-qh88, GO-2026-6365
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65607
Type: osv

## Details
SiYuan before v3.7.2 contains a path traversal vulnerability in the /export/temp/ short-circuit branch of the serveExport handler (kernel/server/serve.go). Unlike the main export branch, this branch joins the raw, percent-decoded request path with util.TempDir and serves the file without the IsSubPath or IsSensitivePath checks added in the earlier export-disclosure hardening (GHSA-6865-qjcf-286f). An authenticated attacker can send percent-encoded traversal sequences (e.g. /export/temp/%2e%2e/.../etc/passwd, where %2e%2e is decoded to '..') to read arbitrary files outside TempDir, including /etc/passwd, SSH keys (~/.ssh/*), and SiYuan workspace *.db and *.log files, bypassing the sensitive-file protection.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65607.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-gw25-m53r-qh88
- https://nvd.nist.gov/vuln/detail/CVE-2026-65607
- https://www.vulncheck.com/advisories/siyuan-before-path-traversal-via-export-temp
- https://github.com/siyuan-note/siyuan/commit/bb481e1290c4a34255652ede85a546504505d2a7
