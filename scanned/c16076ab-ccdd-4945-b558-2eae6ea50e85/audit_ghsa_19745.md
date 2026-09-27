# [H] jwt-go allows excessive memory allocation during header parsing

## Summary
Severity: High
Advisory: GHSA-mh63-6h87-95cp
CVE: CVE-2025-30204
CWE: CWE-405
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-03-21
Source: https://github.com/advisories/GHSA-mh63-6h87-95cp
Type: github-advisory

## Affected
- Go: `github.com/golang-jwt/jwt/v5` — affected >=5.0.0-rc.1 <5.2.2
- Go: `github.com/golang-jwt/jwt/v4` — affected >=0 <4.5.2
- Go: `github.com/golang-jwt/jwt` — affected >=3.2.0

## Details
### Summary

Function [`parse.ParseUnverified`](https://github.com/golang-jwt/jwt/blob/c035977d9e11c351f4c05dfeae193923cbab49ee/parser.go#L138-L139) currently splits (via a call to [strings.Split](https://pkg.go.dev/strings#Split)) its argument (which is untrusted data) on periods.

As a result, in the face of a malicious request whose _Authorization_ header consists of `Bearer ` followed by many period characters, a call to that function incurs allocations to the tune of O(n) bytes (where n stands for the length of the function's argument), with a constant factor of about 16. Relevant weakness: [CWE-405: Asymmetric Resource Consumption (Amplification)](https://cwe.mitre.org/data/definitions/405.html)

### Details

See [`parse.ParseUnverified`](https://github.com/golang-jwt/jwt/blob/c035977d9e11c351f4c05dfeae193923cbab49ee/parser.go#L138-L139) 

### Impact

Excessive memory allocation

## References
- https://github.com/golang-jwt/jwt/security/advisories/GHSA-mh63-6h87-95cp
- https://nvd.nist.gov/vuln/detail/CVE-2025-30204
- https://github.com/golang-jwt/jwt/commit/0951d184286dece21f73c85673fd308786ffe9c3
- https://github.com/golang-jwt/jwt/commit/bf316c48137a1212f8d0af9288cc9ce8e59f1afb
- https://github.com/golang-jwt/jwt
- https://security.netapp.com/advisory/ntap-20250404-0002
