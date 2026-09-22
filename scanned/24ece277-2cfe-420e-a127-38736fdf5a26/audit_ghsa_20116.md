# [H] robbert229/jwt's token validation methods vulnerable to a timing side-channel during HMAC comparison

## Summary
Severity: High
Advisory: GHSA-5vw4-v588-pgv8
CVE: CVE-2015-10004
CWE: CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-5vw4-v588-pgv8
Type: github-advisory

## Affected
- Go: `github.com/robbert229/jwt` — affected >=0 <0.0.0-20170426191122-ca1404ee6e83

## Details
Token validation methods are susceptible to a timing side-channel during HMAC comparison. With a large enough number of requests over a low latency connection, an attacker may use this to determine the expected HMAC.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-10004
- https://github.com/robbert229/jwt/issues/12
- https://github.com/robbert229/jwt/commit/ca1404ee6e83fcbafb66b09ed0d543850a15b654
- https://github.com/robbert229/jwt
- https://pkg.go.dev/vuln/GO-2020-0023
