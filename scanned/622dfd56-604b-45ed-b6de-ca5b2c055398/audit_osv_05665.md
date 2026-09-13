# [M] ALPN negotiation error contains attacker controlled information in crypto/tls

## Summary
Severity: Medium
Advisory: BIT-golang-2025-58189
Aliases: CVE-2025-58189, GO-2025-4008
Ecosystem: Bitnami
Published: 2025-11-06
Source: https://osv.dev/vulnerability/BIT-golang-2025-58189
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.2

## Details
When Conn.Handshake fails during ALPN negotiation the error contains attacker controlled information (the ALPN protocols sent by the client) which is not escaped.

## References
- http://www.openwall.com/lists/oss-security/2025/10/08/1
- https://go.dev/cl/707776
- https://go.dev/issue/75652
- https://groups.google.com/g/golang-announce/c/4Emdl2iQ_bI
- https://nvd.nist.gov/vuln/detail/CVE-2025-58189
- https://pkg.go.dev/vuln/GO-2025-4008
