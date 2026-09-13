# [H] NUL character in ROA causes OctoRPKI to crash

## Summary
Severity: High
Advisory: GHSA-5mxh-2qfv-4g7j
CVE: CVE-2021-3910
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-5mxh-2qfv-4g7j
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cfrpki` — affected >=0 <1.4.0

## Details
OctoRPKI crashes when encountering a repository that returns an invalid ROA (just an encoded `NUL` (`\0`) character).

## Patches

## For more information
If you have any questions or comments about this advisory email us at security@cloudflare.com

## References
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-5mxh-2qfv-4g7j
- https://nvd.nist.gov/vuln/detail/CVE-2021-3910
- https://github.com/cloudflare/cfrpki/commit/76f0f7a98da001fa04e5bc0407c6702f91096bfa
- https://github.com/cloudflare/cfrpki
- https://github.com/cloudflare/cfrpki/releases/tag/v1.4.0
- https://pkg.go.dev/vuln/GO-2022-0251
- https://www.debian.org/security/2022/dsa-5041
