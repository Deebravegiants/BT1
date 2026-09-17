# [H] Memory exhaustion in QUIC connection handling in crypto/tls

## Summary
Severity: High
Advisory: BIT-golang-2023-39322
Aliases: CVE-2023-39322, GO-2023-2045
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-39322
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.21.0 <1.21.1

## Details
QUIC connections do not set an upper bound on the amount of data buffered when reading post-handshake messages, allowing a malicious QUIC connection to cause unbounded memory growth. With fix, connections now consistently reject messages larger than 65KiB in size.

## References
- https://go.dev/cl/523039
- https://go.dev/issue/62266
- https://groups.google.com/g/golang-dev/c/2C5vbR-UNkI/m/L1hdrPhfBAAJ
- https://pkg.go.dev/vuln/GO-2023-2045
- https://security.gentoo.org/glsa/202311-09
- https://security.netapp.com/advisory/ntap-20231020-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2023-39322
