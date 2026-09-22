# [M] Handshake messages may be processed at the incorrect encryption level in crypto/tls

## Summary
Severity: Medium
Advisory: BIT-golang-2025-61730
Aliases: CVE-2025-61730, GO-2026-4340
Ecosystem: Bitnami
Published: 2026-01-31
Source: https://osv.dev/vulnerability/BIT-golang-2025-61730
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.25.0 <1.25.6

## Details
During the TLS 1.3 handshake if multiple messages are sent in records that span encryption level boundaries (for instance the Client Hello and Encrypted Extensions messages), the subsequent messages may be processed before the encryption level changes. This can cause some minor information disclosure if a network-local attacker can inject messages during the handshake.

## References
- https://go.dev/cl/724120
- https://go.dev/issue/76443
- https://groups.google.com/g/golang-announce/c/Vd2tYVM8eUc
- https://nvd.nist.gov/vuln/detail/CVE-2025-61730
- https://pkg.go.dev/vuln/GO-2026-4340
