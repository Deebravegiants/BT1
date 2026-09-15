# [H] Before Go 1.20, the RSA based key exchange methods in crypto/tls may exhibit a timing side channel

## Summary
Severity: High
Advisory: BIT-golang-2023-45287
Aliases: CVE-2023-45287, GO-2023-2375
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-45287
Type: osv

## Affected
- Bitnami: `golang` — affected >=0 <1.20.0

## Details
Before Go 1.20, the RSA based TLS key exchanges used the math/big library, which is not constant time. RSA blinding was applied to prevent timing attacks, but analysis shows this may not have been fully effective. In particular it appears as if the removal of PKCS#1 padding may leak timing information, which in turn could be used to recover session key bits. In Go 1.20, the crypto/tls library switched to a fully constant time RSA implementation, which we do not believe exhibits any timing side channels.

## References
- https://go.dev/cl/326012/26
- https://go.dev/issue/20654
- https://groups.google.com/g/golang-announce/c/QMK8IQALDvA
- https://people.redhat.com/~hkario/marvin/
- https://pkg.go.dev/vuln/GO-2023-2375
- https://security.netapp.com/advisory/ntap-20240112-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2023-45287
