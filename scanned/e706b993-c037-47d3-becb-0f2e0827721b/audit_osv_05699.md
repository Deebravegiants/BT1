# [M] Invoking Encrypted Client Hello privacy leak in crypto/tls

## Summary
Severity: Medium
Advisory: BIT-golang-2026-42505
Aliases: CVE-2026-42505, GO-2026-5856
Ecosystem: Bitnami
Published: 2026-07-14
Source: https://osv.dev/vulnerability/BIT-golang-2026-42505
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.27.0-0 <1.27.0

## Details
Handshakes which used Encrypted Client Hello could be de-anonymized by a passive network observer due to a disclosure of pre-shared key identities in the unencrypted client hello.

## References
- https://go.dev/cl/775960
- https://go.dev/issue/79282
- https://groups.google.com/g/golang-announce/c/OrmQE_Yp5Sc
- https://nvd.nist.gov/vuln/detail/CVE-2026-42505
- https://pkg.go.dev/vuln/GO-2026-5856
