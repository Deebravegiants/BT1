# [H] Integer Overflow in go-jose

## Summary
Severity: High
Advisory: GHSA-3fx4-7f69-5mmg
CVE: CVE-2016-9123
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-23
Source: https://github.com/advisories/GHSA-3fx4-7f69-5mmg
Type: github-advisory

## Affected
- Go: `github.com/square/go-jose` — affected >=0 <0.0.0-20160903044734-789a4c4bd4c1

## Details
go-jose before 1.0.5 suffers from a CBC-HMAC integer overflow on 32-bit architectures. An integer overflow could lead to authentication bypass for CBC-HMAC encrypted ciphertexts on 32-bit architectures.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-9123
- https://github.com/square/go-jose/commit/789a4c4bd4c118f7564954f441b29c153ccd6a96
- https://hackerone.com/reports/165170
- https://pkg.go.dev/vuln/GO-2020-0009
- https://www.openwall.com/lists/oss-security/2016/11/03/1
