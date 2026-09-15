# [M] jose2go vulnerable to denial of service via large p2c value

## Summary
Severity: Medium
Advisory: GHSA-6294-6rgp-fr7r
CVE: CVE-2023-50658
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-6294-6rgp-fr7r
Type: github-advisory

## Affected
- Go: `github.com/dvsekhvalnov/jose2go` — affected >=0 <1.6.0

## Details
The jose2go component before 1.6.0 for Go allows attackers to cause a denial of service (CPU consumption) via a large p2c (aka PBES2 Count) value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50658
- https://github.com/dvsekhvalnov/jose2go/issues/31
- https://github.com/dvsekhvalnov/jose2go/commit/a4584e9dd7128608fedbc67892eba9697f0d5317
- https://github.com/dvsekhvalnov/jose2go
- https://github.com/dvsekhvalnov/jose2go/compare/v1.5.0...v1.6.0
- https://pkg.go.dev/vuln/GO-2023-2409
- https://www.blackhat.com/us-23/briefings/schedule/#three-new-attacks-against-json-web-tokens-31695
