# [H] SiYuan has an arbitrary file write in the host via /api/asset/upload

## Summary
Severity: High
Advisory: GHSA-fqj6-whhx-47p7
CVE: CVE-2024-55659
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-11
Source: https://github.com/advisories/GHSA-fqj6-whhx-47p7
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary

The /api/asset/upload endpoint in Siyuan is vulnerable to both arbitrary file write to the host and stored XSS (via the file write).

### Impact
Arbitrary file write

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-fqj6-whhx-47p7
- https://nvd.nist.gov/vuln/detail/CVE-2024-55659
- https://github.com/siyuan-note/siyuan/commit/e70ed57f6e4852e2bd702671aeb8eb3a47a36d71
- https://github.com/siyuan-note/siyuan
- https://pkg.go.dev/vuln/GO-2024-3326
