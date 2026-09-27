# [M] SiYuan before v3.8.2 Path Traversal via symlink in file API

## Summary
Severity: Medium
Advisory: CVE-2026-85583
Aliases: GHSA-g7gf-v79m-jwrm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85583
Type: osv

## Details
SiYuan versions before v3.8.2 contain a path traversal vulnerability in the reader-accessible file-read endpoint that follows symlinks when opening authorized asset paths. Attackers with reader role can request a logical asset under data/assets/ that is a symlink to a file outside the workspace and receive the target file bytes, bypassing workspace boundary restrictions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85583.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-g7gf-v79m-jwrm
- https://nvd.nist.gov/vuln/detail/CVE-2026-85583
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-path-traversal-via-symlink-in-file-api
