# [M] Sensitive headers incorrectly sent after cross-domain redirect in net/http

## Summary
Severity: Medium
Advisory: BIT-golang-2024-45336
Aliases: CVE-2024-45336, GO-2025-3420
Ecosystem: Bitnami
Published: 2025-01-30
Source: https://osv.dev/vulnerability/BIT-golang-2024-45336
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0-0 <1.24.0

## Details
The HTTP client drops sensitive headers after following a cross-domain redirect. For example, a request to a.com/ containing an Authorization header which is redirected to b.com/ will not send that header to b.com. In the event that the client received a subsequent same-domain redirect, however, the sensitive headers would be restored. For example, a chain of redirects from a.com/, to b.com/1, and finally to b.com/2 would incorrectly send the Authorization header to b.com/2.

## References
- https://go.dev/cl/643100
- https://go.dev/issue/70530
- https://groups.google.com/g/golang-dev/c/CAWXhan3Jww/m/bk9LAa-lCgAJ
- https://groups.google.com/g/golang-dev/c/bG8cv1muIBM/m/G461hA6lCgAJ
- https://pkg.go.dev/vuln/GO-2025-3420
- https://security.netapp.com/advisory/ntap-20250221-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2024-45336
