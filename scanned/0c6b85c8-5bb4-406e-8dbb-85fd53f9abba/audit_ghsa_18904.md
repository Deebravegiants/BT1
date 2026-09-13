# [H] jose2go is vulnerable to a JWT bomb attack through its decode function

## Summary
Severity: High
Advisory: GHSA-9mj6-hxhv-w67j
CVE: CVE-2025-63811
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-12
Source: https://github.com/advisories/GHSA-9mj6-hxhv-w67j
Type: github-advisory

## Affected
- Go: `github.com/dvsekhvalnov/jose2go` — affected >=0 <1.7.0

## Details
An issue was discovered in dvsekhvalnov jose2go 1.5.0 thru 1.7.0 allowing an attacker to cause a Denial-of-Service (DoS) via crafted JSON Web Encryption (JWE) token with an exceptionally high compression ratio.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-63811
- https://github.com/dvsekhvalnov/jose2go/issues/33
- https://github.com/dvsekhvalnov/jose2go/commit/0a0673dd7f2820a446de5b04b9094b2291d77d5d
- https://github.com/dvsekhvalnov/jose2go
