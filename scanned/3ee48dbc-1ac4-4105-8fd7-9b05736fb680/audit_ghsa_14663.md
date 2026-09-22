# [H] SiYuan has an arbitrary file read and path traversal via /api/export/exportResources

## Summary
Severity: High
Advisory: GHSA-25w9-wqfq-gwqx
CVE: CVE-2024-55658
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-11
Source: https://github.com/advisories/GHSA-25w9-wqfq-gwqx
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary

Siyuan's /api/export/exportResources endpoint is vulnerable to arbitary file read via path traversal. It is possible to manipulate the paths parameter to access and download arbitrary files from the host system by traversing the workspace directory structure.

### Impact
Arbitrary File Read

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-25w9-wqfq-gwqx
- https://nvd.nist.gov/vuln/detail/CVE-2024-55658
- https://github.com/siyuan-note/siyuan/commit/e70ed57f6e4852e2bd702671aeb8eb3a47a36d71
- https://github.com/siyuan-note/siyuan
- https://pkg.go.dev/vuln/GO-2024-3323
