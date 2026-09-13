# [M] Verify panics on certificates with an unknown public key algorithm in crypto/x509

## Summary
Severity: Medium
Advisory: BIT-golang-2024-24783
Aliases: CVE-2024-24783, GO-2024-2598
Ecosystem: Bitnami
Published: 2024-03-12
Source: https://osv.dev/vulnerability/BIT-golang-2024-24783
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.22.0-0 <1.22.1

## Details
Verifying a certificate chain which contains a certificate with an unknown public key algorithm will cause Certificate.Verify to panic. This affects all crypto/tls clients, and servers that set Config.ClientAuth to VerifyClientCertIfGiven or RequireAndVerifyClientCert. The default behavior is for TLS servers to not verify client certificates.

## References
- https://go.dev/cl/569339
- https://go.dev/issue/65390
- https://groups.google.com/g/golang-announce/c/5pwGVUPoMbg
- https://pkg.go.dev/vuln/GO-2024-2598
- https://security.netapp.com/advisory/ntap-20240329-0005/
- http://www.openwall.com/lists/oss-security/2024/03/08/4
- https://nvd.nist.gov/vuln/detail/CVE-2024-24783
