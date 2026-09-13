# [H] SiYuan has an arbitrary file read via /api/template/render

## Summary
Severity: High
Advisory: GHSA-xx68-37v4-4596
CVE: CVE-2024-55657
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-12-11
Source: https://github.com/advisories/GHSA-xx68-37v4-4596
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary

An arbitrary file read vulnerability exists in Siyuan's /api/template/render endpoint. The absence of proper validation on the path parameter allows attackers to access sensitive files on the host system.

### Impact

Arbitrary file read on the host

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-xx68-37v4-4596
- https://nvd.nist.gov/vuln/detail/CVE-2024-55657
- https://github.com/siyuan-note/siyuan/commit/e70ed57f6e4852e2bd702671aeb8eb3a47a36d71
- https://github.com/siyuan-note/siyuan
- https://pkg.go.dev/vuln/GO-2024-3327
