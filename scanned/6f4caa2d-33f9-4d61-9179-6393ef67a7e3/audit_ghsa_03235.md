# [H] Ory fosite contains Improper Handling of Exceptional Conditions 

## Summary
Severity: High
Advisory: GHSA-7mqr-2v3q-v2wm
CVE: CVE-2020-15223
CWE: CWE-754, CWE-755
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-7mqr-2v3q-v2wm
Type: github-advisory

## Affected
- Go: `github.com/ory/fosite` — affected >=0 <0.34.0

## Details
### Impact
The `TokenRevocationHandler` ignores errors coming from the storage. This can lead to unexpected 200 status codes indicating successful revocation while the token is still valid. Whether an attacker can use this for her advantage depends on the ability to trigger errors in the store.

### References
[RFC 7009](https://tools.ietf.org/html/rfc7009#section-2.2.1) states that a 503 HTTP code must be returned when the server has a problem.

## References
- https://github.com/ory/fosite/security/advisories/GHSA-7mqr-2v3q-v2wm
- https://nvd.nist.gov/vuln/detail/CVE-2020-15223
- https://github.com/ory/fosite/commit/03dd55813f5521985f7dd64277b7ba0cf1441319
- https://pkg.go.dev/vuln/GO-2021-0109
- https://tools.ietf.org/html/rfc7009#section-2.2.1
