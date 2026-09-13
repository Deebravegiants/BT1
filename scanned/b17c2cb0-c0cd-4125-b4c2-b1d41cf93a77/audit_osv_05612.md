# [H] Panic on large handshake records in crypto/tls

## Summary
Severity: High
Advisory: BIT-golang-2022-41724
Aliases: CVE-2022-41724, GO-2023-1570
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2022-41724
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.1

## Details
Large handshake records may cause panics in crypto/tls. Both clients and servers may send large TLS handshake records which cause servers and clients, respectively, to panic when attempting to construct responses. This affects all TLS 1.3 clients, TLS 1.2 clients which explicitly enable session resumption (by setting Config.ClientSessionCache to a non-nil value), and TLS 1.3 servers which request client certificates (by setting Config.ClientAuth >= RequestClientCert).

## References
- https://go.dev/cl/468125
- https://go.dev/issue/58001
- https://groups.google.com/g/golang-announce/c/V0aBFqaFs_E
- https://pkg.go.dev/vuln/GO-2023-1570
- https://security.gentoo.org/glsa/202311-09
- https://nvd.nist.gov/vuln/detail/CVE-2022-41724
