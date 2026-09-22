# [H] golang.org/x/crypto Vulnerable to Denial of Service (DoS) via Slow or Incomplete Key Exchange

## Summary
Severity: High
Advisory: GHSA-hcg3-q754-cr77
CVE: CVE-2025-22869
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-12
Source: https://github.com/advisories/GHSA-hcg3-q754-cr77
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.35.0

## Details
SSH servers which implement file transfer protocols are vulnerable to a denial of service attack from clients which complete the key exchange slowly, or not at all, causing pending content to be read into memory, but never transmitted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-22869
- https://github.com/golang/crypto/commit/7292932d45d55c7199324ab0027cc86e8198aa22
- https://github.com/golang/crypto
- https://go-review.googlesource.com/c/crypto/+/652135
- https://go.dev/cl/652135
- https://go.dev/issue/71931
- https://pkg.go.dev/vuln/GO-2025-3487
- https://security.netapp.com/advisory/ntap-20250411-0010
