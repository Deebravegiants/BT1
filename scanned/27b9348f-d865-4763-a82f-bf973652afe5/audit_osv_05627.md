# [M] Large RSA keys can cause high CPU usage in crypto/tls

## Summary
Severity: Medium
Advisory: BIT-golang-2023-29409
Aliases: CVE-2023-29409, GO-2023-1987
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2023-29409
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.20.0 <1.20.7

## Details
Extremely large RSA keys in certificate chains can cause a client/server to expend significant CPU time verifying signatures. With fix, the size of RSA keys transmitted during handshakes is restricted to <= 8192 bits. Based on a survey of publicly trusted RSA keys, there are currently only three certificates in circulation with keys larger than this, and all three appear to be test certificates that are not actively deployed. It is possible there are larger keys in use in private PKIs, but we target the web PKI, so causing breakage here in the interests of increasing the default safety of users of crypto/tls seems reasonable.

## References
- https://go.dev/cl/515257
- https://go.dev/issue/61460
- https://groups.google.com/g/golang-announce/c/X0b6CsSAaYI/m/Efv5DbZ9AwAJ
- https://pkg.go.dev/vuln/GO-2023-1987
- https://security.gentoo.org/glsa/202311-09
- https://security.netapp.com/advisory/ntap-20230831-0010/
- https://nvd.nist.gov/vuln/detail/CVE-2023-29409
