# [M] SiYuan has an SSTI via /api/template/renderSprig

## Summary
Severity: Medium
Advisory: GHSA-4pjc-pwgq-q9jp
CVE: CVE-2024-55660
CWE: CWE-1336
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-11
Source: https://github.com/advisories/GHSA-4pjc-pwgq-q9jp
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary
Siyuan's /api/template/renderSprig endpoint is vulnerable to Server-Side Template Injection (SSTI) through the Sprig template engine. Although the engine has limitations, it allows attackers to access environment variables

### Impact

Information leakage

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-4pjc-pwgq-q9jp
- https://nvd.nist.gov/vuln/detail/CVE-2024-55660
- https://github.com/siyuan-note/siyuan/commit/e70ed57f6e4852e2bd702671aeb8eb3a47a36d71
- https://github.com/siyuan-note/siyuan
- https://pkg.go.dev/vuln/GO-2024-3324
