# [M] usememos/memos may leak user information to an authenticated user

## Summary
Severity: Medium
Advisory: GHSA-j593-h5v3-45x6
CVE: CVE-2022-4734
CWE: CWE-200, CWE-212
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-12-27
Source: https://github.com/advisories/GHSA-j593-h5v3-45x6
Type: github-advisory

## Affected
- Go: `github.com/usememos/memos` — affected >=0 <0.9.1

## Details
usememos/memos 0.9.0 and prior has endpoint that leaks user information like names, email, role, and OpenID to an authenticated user. A patch is available at commit 05b41804e33a34102f1f75bb2d69195dda6a1210 on the `main` branch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4734
- https://github.com/usememos/memos/commit/05b41804e33a34102f1f75bb2d69195dda6a1210
- https://github.com/usememos/memos
- https://huntr.dev/bounties/4b4421dc-73af-4dec-884c-836f9732cb5b
